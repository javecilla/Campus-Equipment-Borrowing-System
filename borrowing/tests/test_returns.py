"""T17 PostgreSQL integration through approval/release, returns, maintenance and HTTP."""

from datetime import date, timedelta

from django.core.exceptions import PermissionDenied, ValidationError
from django.db import IntegrityError, connection
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from accounts.models import User, UserRole
from borrowing.models import (
    BorrowRequest,
    Loan,
    LoanUnit,
    RequestStatus,
    ReturnRecord,
    UnitAllocation,
)
from borrowing.queries import manage_loan_history, with_loan_progress
from borrowing.release_services import release_request
from borrowing.return_services import ReturnInput, return_units
from borrowing.services import WorkflowConflict, approve_request
from inventory.models import (
    EquipmentUnit,
    MaintenanceOutcome,
    MaintenanceRecord,
    MaintenanceStatus,
    UnitCondition,
    UnitStatus,
)
from inventory.services import close_maintenance
from operations.models import AuditAction, AuditLog, AuditTarget
from operations.tests.records import CatalogRecords, create_catalog_records, create_request


def create_return_loan(records: CatalogRecords) -> Loan:
    """Use the actual accepted workflows, with two physical units on one issued loan."""
    EquipmentUnit.objects.create(
        catalog_item=records.item,
        asset_code="T17-CAM-002",
        condition=UnitCondition.GOOD,
        acquired_on=timezone.localdate(),
        status=UnitStatus.AVAILABLE,
    )
    line = create_request(records.borrower.pk, records.item.pk, timezone.now())
    line.quantity = 2
    line.save(update_fields=["quantity"])
    approve_request(records.admin.pk, line.request_id, "T17 approval")
    return release_request(records.admin.pk, line.request_id)


def return_payload(rows: tuple[ReturnInput, ...]) -> dict[str, str]:
    payload: dict[str, str] = {
        "returns-TOTAL_FORMS": str(len(rows)),
        "returns-INITIAL_FORMS": str(len(rows)),
        "returns-MIN_NUM_FORMS": "0",
        "returns-MAX_NUM_FORMS": str(len(rows)),
    }
    for index, row in enumerate(rows):
        payload.update(
            {
                f"returns-{index}-selected": "on",
                f"returns-{index}-loan_unit": str(row.loan_unit_id),
                f"returns-{index}-returned_condition": row.returned_condition,
                f"returns-{index}-notes": row.notes,
                f"returns-{index}-maintenance_problem": row.maintenance_problem,
            }
        )
    return payload


class ReturnTestBase(TestCase):
    records: CatalogRecords
    loan: Loan
    first: LoanUnit
    second: LoanUnit

    @classmethod
    def setUpTestData(cls) -> None:
        cls.records = create_catalog_records()
        cls.loan = create_return_loan(cls.records)
        cls.first, cls.second = tuple(cls.loan.units.order_by("pk"))

    def assert_unreturned(self) -> None:
        self.loan.refresh_from_db()
        self.loan.request.refresh_from_db()
        self.assertIsNone(self.loan.closed_at)
        self.assertEqual(self.loan.request.status, RequestStatus.ISSUED)
        self.assertFalse(ReturnRecord.objects.exists())
        self.assertFalse(MaintenanceRecord.objects.exists())
        self.assertEqual(EquipmentUnit.objects.filter(status=UnitStatus.ISSUED).count(), 2)
        self.assertFalse(UnitAllocation.objects.filter(ended_at__isnull=False).exists())
        self.assertFalse(
            AuditLog.objects.filter(
                action__in=(AuditAction.UNIT_RETURNED, AuditAction.MAINTENANCE_OPENED)
            ).exists()
        )


class ReturnServiceTests(ReturnTestBase):
    def test_partial_then_final_damaged_return_and_repair_reconcile_inventory(self) -> None:
        before = timezone.now()
        return_units(
            self.records.admin.pk,
            self.loan.pk,
            (ReturnInput(self.first.pk, UnitCondition.FAIR, " Checked ", ""),),
        )
        self.loan.refresh_from_db()
        self.loan.request.refresh_from_db()
        self.assertIsNone(self.loan.closed_at)
        self.assertEqual(self.loan.request.status, RequestStatus.PARTIALLY_RETURNED)
        first_return = ReturnRecord.objects.get(loan_unit=self.first)
        self.assertGreaterEqual(first_return.returned_at, before)
        self.assertEqual(first_return.received_by_id, self.records.admin.pk)
        self.assertEqual(first_return.notes, "Checked")
        first_allocation = UnitAllocation.objects.get(pk=self.first.allocation_id)
        first_unit = first_allocation.unit
        self.assertEqual(first_allocation.ended_at, first_return.returned_at)
        self.assertIsNotNone(first_allocation.released_at)
        self.assertIsNone(first_allocation.cancelled_at)
        self.assertEqual(
            (first_unit.status, first_unit.condition), (UnitStatus.AVAILABLE, UnitCondition.FAIR)
        )
        self.assertEqual(EquipmentUnit.objects.filter(status=UnitStatus.ISSUED).count(), 1)

        return_units(
            self.records.admin.pk,
            self.loan.pk,
            (
                ReturnInput(
                    self.second.pk, UnitCondition.DAMAGED, "Private inspection", " Cracked lens "
                ),
            ),
        )
        self.loan.refresh_from_db()
        self.loan.request.refresh_from_db()
        final_return = ReturnRecord.objects.get(loan_unit=self.second)
        maintenance = MaintenanceRecord.objects.get(source_return=final_return)
        self.assertEqual(self.loan.closed_at, final_return.returned_at)
        self.assertEqual(self.loan.request.status, RequestStatus.RETURNED)
        self.assertEqual(maintenance.unit_id, self.second.allocation.unit_id)
        self.assertEqual(maintenance.status, MaintenanceStatus.OPEN)
        self.assertEqual(maintenance.opened_at, final_return.returned_at)
        self.assertEqual(maintenance.opened_by_id, self.records.admin.pk)
        self.assertEqual(maintenance.problem, "Cracked lens")
        self.assertEqual(maintenance.unit.status, UnitStatus.MAINTENANCE)
        self.assertEqual(maintenance.unit.condition, UnitCondition.DAMAGED)
        self.assertEqual(AuditLog.objects.filter(action=AuditAction.UNIT_RETURNED).count(), 2)
        self.assertTrue(
            AuditLog.objects.filter(
                actor_id=self.records.admin.pk,
                action=AuditAction.MAINTENANCE_OPENED,
                target_model=AuditTarget.MAINTENANCE_RECORD,
                target_id=maintenance.pk,
            ).exists()
        )
        close_maintenance(
            self.records.admin.pk,
            maintenance.pk,
            "Replaced lens",
            MaintenanceOutcome.AVAILABLE,
            UnitCondition.GOOD,
        )
        self.assertEqual(EquipmentUnit.objects.filter(status=UnitStatus.AVAILABLE).count(), 2)
        self.assertEqual(UnitAllocation.objects.filter(ended_at__isnull=True).count(), 0)

    def test_batch_mixed_conditions_closes_once_and_allows_new_reservation(self) -> None:
        rows = (
            ReturnInput(self.first.pk, UnitCondition.GOOD, "", ""),
            ReturnInput(self.second.pk, UnitCondition.DAMAGED, "", "Broken mount"),
        )
        returned_loan = return_units(self.records.admin.pk, self.loan.pk, rows)
        self.assertIsNotNone(returned_loan.closed_at)
        self.assertEqual(ReturnRecord.objects.count(), 2)
        self.assertEqual(ReturnRecord.objects.values("returned_at").distinct().count(), 1)
        new_line = create_request(self.records.borrower.pk, self.records.item.pk, timezone.now())
        approve_request(self.records.admin.pk, new_line.request_id, "Reborrow returned good unit")
        self.assertEqual(EquipmentUnit.objects.filter(status=UnitStatus.RESERVED).count(), 1)
        self.assertEqual(EquipmentUnit.objects.filter(status=UnitStatus.MAINTENANCE).count(), 1)
        self.assertEqual(UnitAllocation.objects.filter(ended_at__isnull=True).count(), 1)

    def test_invalid_selection_condition_duplicate_and_blank_problem_write_nothing(self) -> None:
        good = ReturnInput(self.first.pk, UnitCondition.GOOD, "", "")
        cases = (
            (),
            (good, good),
            (good, ReturnInput(self.second.pk, "RETIRED", "", "")),
            (good, ReturnInput(self.second.pk, UnitCondition.DAMAGED, "", "  ")),
            (ReturnInput(-1, UnitCondition.GOOD, "", ""),),
        )
        for rows in cases:
            with self.subTest(rows=rows), self.assertRaises(ValidationError):
                return_units(self.records.admin.pk, self.loan.pk, rows)
            self.assert_unreturned()

    def test_foreign_loan_unit_rejects_entire_selection(self) -> None:
        other_line = create_request(self.records.borrower.pk, self.records.item.pk, timezone.now())
        other_loan = Loan.objects.create(
            request=other_line.request,
            issued_by=self.records.admin,
            issued_at=timezone.now(),
            issued_on=timezone.localdate(),
            due_date=other_line.request.agreed_due_date,
        )
        with self.assertRaises(WorkflowConflict):
            return_units(
                self.records.admin.pk,
                other_loan.pk,
                (ReturnInput(self.first.pk, UnitCondition.GOOD, "", ""),),
            )
        self.assert_unreturned()

    def test_stale_duplicate_cannot_return_the_other_unit_partially(self) -> None:
        first = ReturnInput(self.first.pk, UnitCondition.GOOD, "", "")
        return_units(self.records.admin.pk, self.loan.pk, (first,))
        with self.assertRaises(WorkflowConflict):
            return_units(
                self.records.admin.pk,
                self.loan.pk,
                (
                    ReturnInput(self.second.pk, UnitCondition.GOOD, "", ""),
                    first,
                ),
            )
        self.assertEqual(ReturnRecord.objects.count(), 1)
        self.loan.refresh_from_db()
        self.assertIsNone(self.loan.closed_at)

    def test_return_requires_active_admin_even_when_called_directly(self) -> None:
        rows = (ReturnInput(self.first.pk, UnitCondition.GOOD, "", ""),)
        for actor_id in (self.records.borrower.pk, 999999):
            with self.assertRaises(PermissionDenied):
                return_units(actor_id, self.loan.pk, rows)
        User.objects.filter(pk=self.records.admin.pk).update(is_active=False)
        with self.assertRaises(PermissionDenied):
            return_units(self.records.admin.pk, self.loan.pk, rows)
        self.assert_unreturned()

    def test_archived_catalog_and_inactive_borrower_do_not_strand_issued_units(self) -> None:
        self.records.category.is_archived = True
        self.records.category.save(update_fields=["is_archived"])
        self.records.item.is_archived = True
        self.records.item.save(update_fields=["is_archived"])
        User.objects.filter(pk=self.records.borrower.pk).update(is_active=False)
        return_units(
            self.records.admin.pk,
            self.loan.pk,
            (ReturnInput(self.first.pk, UnitCondition.GOOD, "", ""),),
        )
        self.assertEqual(ReturnRecord.objects.count(), 1)

    def test_nonissued_request_states_are_conflicts(self) -> None:
        for status in (
            RequestStatus.PENDING,
            RequestStatus.APPROVED,
            RequestStatus.REJECTED,
            RequestStatus.CANCELLED,
            RequestStatus.RETURNED,
        ):
            BorrowRequest.objects.filter(pk=self.loan.request_id).update(status=status)
            with self.subTest(status=status), self.assertRaises(WorkflowConflict):
                return_units(
                    self.records.admin.pk,
                    self.loan.pk,
                    (ReturnInput(self.first.pk, UnitCondition.GOOD, "", ""),),
                )
        self.assertFalse(ReturnRecord.objects.exists())

    def test_ended_allocation_wrong_status_and_open_maintenance_are_conflicts(self) -> None:
        rows = (ReturnInput(self.first.pk, UnitCondition.GOOD, "", ""),)
        UnitAllocation.objects.filter(pk=self.first.allocation_id).update(ended_at=timezone.now())
        with self.assertRaises(WorkflowConflict):
            return_units(self.records.admin.pk, self.loan.pk, rows)
        UnitAllocation.objects.filter(pk=self.first.allocation_id).update(ended_at=None)
        for status in (
            UnitStatus.AVAILABLE,
            UnitStatus.RESERVED,
            UnitStatus.MAINTENANCE,
            UnitStatus.RETIRED,
        ):
            EquipmentUnit.objects.filter(pk=self.first.allocation.unit_id).update(status=status)
            with self.subTest(status=status), self.assertRaises(WorkflowConflict):
                return_units(self.records.admin.pk, self.loan.pk, rows)
        EquipmentUnit.objects.filter(pk=self.first.allocation.unit_id).update(
            status=UnitStatus.ISSUED
        )
        MaintenanceRecord.objects.create(
            unit_id=self.first.allocation.unit_id,
            problem="Corrupt fixture",
            opened_at=timezone.now(),
            opened_by=self.records.admin,
            status=MaintenanceStatus.OPEN,
        )
        with self.assertRaises(WorkflowConflict):
            return_units(self.records.admin.pk, self.loan.pk, rows)
        self.assertFalse(ReturnRecord.objects.exists())

    def test_inconsistent_item_membership_is_rejected(self) -> None:
        other_line = create_request(self.records.borrower.pk, self.records.item.pk, timezone.now())
        UnitAllocation.objects.filter(pk=self.first.allocation_id).update(request_item=other_line)
        with self.assertRaises(WorkflowConflict):
            return_units(
                self.records.admin.pk,
                self.loan.pk,
                (ReturnInput(self.first.pk, UnitCondition.GOOD, "", ""),),
            )
        self.assert_unreturned()

    def test_server_time_cannot_precede_issue(self) -> None:
        Loan.objects.filter(pk=self.loan.pk).update(issued_at=timezone.now() + timedelta(hours=1))
        with self.assertRaises(WorkflowConflict):
            return_units(
                self.records.admin.pk,
                self.loan.pk,
                (ReturnInput(self.first.pk, UnitCondition.GOOD, "", ""),),
            )
        self.assert_unreturned()

    def test_return_audit_constraint_failure_rolls_back_all_changes(self) -> None:
        with connection.cursor() as cursor:
            cursor.execute("SET CONSTRAINTS ALL IMMEDIATE")
            cursor.execute(
                "ALTER TABLE operations_auditlog ADD CONSTRAINT test_t17_return_audit CHECK (action <> 'UNIT_RETURNED')"
            )
        with self.assertRaises(IntegrityError):
            return_units(
                self.records.admin.pk,
                self.loan.pk,
                (ReturnInput(self.first.pk, UnitCondition.GOOD, "", ""),),
            )
        self.assert_unreturned()

    def test_maintenance_audit_failure_rolls_back_prior_good_return_too(self) -> None:
        with connection.cursor() as cursor:
            cursor.execute("SET CONSTRAINTS ALL IMMEDIATE")
            cursor.execute(
                "ALTER TABLE operations_auditlog ADD CONSTRAINT test_t17_maintenance_audit CHECK (action <> 'MAINTENANCE_OPENED')"
            )
        with self.assertRaises(IntegrityError):
            return_units(
                self.records.admin.pk,
                self.loan.pk,
                (
                    ReturnInput(self.first.pk, UnitCondition.GOOD, "", ""),
                    ReturnInput(self.second.pk, UnitCondition.DAMAGED, "", "Cracked case"),
                ),
            )
        self.assert_unreturned()

    def test_overdue_is_derived_before_on_after_due_partial_and_closed(self) -> None:
        original_status = self.loan.request.status
        for offset, expected in ((-1, 0), (0, 0), (1, 1), (3, 3)):
            today: date = self.loan.due_date + timedelta(days=offset)
            with self.subTest(offset=offset):
                progress = with_loan_progress(Loan.objects.filter(pk=self.loan.pk), today).get()
                self.assertEqual(progress.overdue_days, expected)
                self.assertEqual(progress.is_overdue, expected > 0)
                self.assertEqual(
                    (
                        progress.issued_quantity,
                        progress.returned_quantity,
                        progress.outstanding_quantity,
                    ),
                    (2, 0, 2),
                )
                self.assertTrue(progress.is_active)
        self.loan.request.refresh_from_db()
        self.assertEqual(self.loan.request.status, original_status)
        return_units(
            self.records.admin.pk,
            self.loan.pk,
            (ReturnInput(self.first.pk, UnitCondition.GOOD, "", ""),),
        )
        progress = with_loan_progress(
            Loan.objects.filter(pk=self.loan.pk), self.loan.due_date + timedelta(days=2)
        ).get()
        self.assertEqual(
            (
                progress.issued_quantity,
                progress.returned_quantity,
                progress.outstanding_quantity,
                progress.overdue_days,
            ),
            (2, 1, 1, 2),
        )
        return_units(
            self.records.admin.pk,
            self.loan.pk,
            (ReturnInput(self.second.pk, UnitCondition.GOOD, "", ""),),
        )
        progress = with_loan_progress(
            Loan.objects.filter(pk=self.loan.pk), self.loan.due_date + timedelta(days=2)
        ).get()
        self.assertEqual(
            (
                progress.issued_quantity,
                progress.returned_quantity,
                progress.outstanding_quantity,
                progress.overdue_days,
            ),
            (2, 2, 0, 0),
        )
        self.assertFalse(progress.is_active)
        self.assertFalse(progress.is_overdue)
        self.assertEqual(manage_loan_history("").get(pk=self.loan.pk).returned_quantity, 2)


class ReturnHttpTests(ReturnTestBase):
    def return_url(self) -> str:
        return reverse("borrowing_manage:return-create", args=[self.loan.pk])

    def test_get_is_read_only_and_post_ignores_protected_fields(self) -> None:
        self.client.force_login(self.records.admin)
        page = self.client.get(self.return_url())
        self.assertEqual(page.status_code, 200)
        self.assertContains(page, "T17-CAM-002")
        self.assertEqual(len(page.context["formset"].forms), 2)
        self.assert_unreturned()
        payload = return_payload(
            (ReturnInput(self.first.pk, UnitCondition.FAIR, "Admin observation", ""),)
        )
        payload.update(
            {
                "received_by": str(self.records.borrower.pk),
                "returned_at": "2000-01-01",
                "status": "RETURNED",
                "unit": str(self.second.allocation.unit_id),
            }
        )
        before = timezone.now()
        response = self.client.post(self.return_url(), payload)
        self.assertRedirects(response, reverse("borrowing_manage:loan-detail", args=[self.loan.pk]))
        returned = ReturnRecord.objects.get()
        self.assertEqual(returned.loan_unit_id, self.first.pk)
        self.assertEqual(returned.received_by_id, self.records.admin.pk)
        self.assertGreaterEqual(returned.returned_at, before)
        self.assertEqual(self.client.post(self.return_url(), payload).status_code, 409)
        page = self.client.get(self.return_url())
        self.assertEqual(len(page.context["formset"].forms), 1)

    def test_invalid_second_row_and_formset_tampering_save_nothing(self) -> None:
        self.client.force_login(self.records.admin)
        valid = return_payload(
            (
                ReturnInput(self.first.pk, UnitCondition.GOOD, "", ""),
                ReturnInput(self.second.pk, UnitCondition.DAMAGED, "", ""),
            )
        )
        no_selection = return_payload((ReturnInput(self.first.pk, UnitCondition.GOOD, "", ""),))
        no_selection.pop("returns-0-selected")
        duplicate = return_payload(
            (
                ReturnInput(self.first.pk, UnitCondition.GOOD, "", ""),
                ReturnInput(self.first.pk, UnitCondition.GOOD, "", ""),
            )
        )
        foreign = return_payload((ReturnInput(999999, UnitCondition.GOOD, "", ""),))
        missing_condition = return_payload((ReturnInput(self.first.pk, "", "", ""),))
        too_many = dict(valid, **{"returns-TOTAL_FORMS": "10000"})
        for payload in (valid, no_selection, duplicate, foreign, missing_condition, too_many, {}):
            with self.subTest(payload=payload):
                response = self.client.post(self.return_url(), payload)
                self.assertEqual(response.status_code, 200)
                self.assertFalse(response.context["formset"].is_valid())
                self.assert_unreturned()

    def test_roles_methods_inactive_and_csrf_are_enforced(self) -> None:
        url = self.return_url()
        self.assertEqual(self.client.get(url).status_code, 302)
        self.client.force_login(self.records.borrower)
        self.assertEqual(self.client.get(url).status_code, 403)
        self.assertEqual(self.client.post(url, {}).status_code, 403)
        self.client.force_login(self.records.admin)
        self.assertEqual(self.client.put(url).status_code, 405)
        self.assertEqual(
            self.client.get(reverse("borrowing_manage:return-create", args=[999999])).status_code,
            404,
        )
        csrf_client = Client(enforce_csrf_checks=True)
        csrf_client.force_login(self.records.admin)
        payload = return_payload((ReturnInput(self.first.pk, UnitCondition.GOOD, "", ""),))
        self.assertEqual(csrf_client.post(url, payload).status_code, 403)
        csrf_client.get(url)
        payload["csrfmiddlewaretoken"] = csrf_client.cookies["csrftoken"].value
        self.assertEqual(csrf_client.post(url, payload).status_code, 302)
        User.objects.filter(pk=self.records.admin.pk).update(is_active=False)
        self.assertEqual(self.client.get(url).status_code, 403)
        self.assertEqual(self.client.post(url, payload).status_code, 302)
        self.client.force_login(self.records.admin)
        self.assertEqual(self.client.post(url, payload).status_code, 403)
        self.assertEqual(ReturnRecord.objects.count(), 1)

    def test_final_return_closes_ui_and_portal_hides_notes_and_foreign_history(self) -> None:
        private_note = "PRIVATE-T17-NOTES"
        private_problem = "PRIVATE-T17-MAINTENANCE"
        self.client.force_login(self.records.admin)
        response = self.client.post(
            self.return_url(),
            return_payload(
                (
                    ReturnInput(self.first.pk, UnitCondition.GOOD, private_note, ""),
                    ReturnInput(
                        self.second.pk, UnitCondition.DAMAGED, private_note, private_problem
                    ),
                )
            ),
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.client.get(self.return_url()).status_code, 409)
        self.assertEqual(self.client.post(self.return_url(), {}).status_code, 409)
        detail = self.client.get(reverse("borrowing_manage:loan-detail", args=[self.loan.pk]))
        self.assertContains(detail, "2 / 2 / 0")
        self.assertNotContains(detail, 'data-testid="loan-return-link"')
        self.client.force_login(self.records.borrower)
        for name, identifier in (
            ("loan-detail", self.loan.pk),
            ("request-detail", self.loan.request_id),
        ):
            page = self.client.get(reverse("portal:" + name, args=[identifier]))
            self.assertContains(page, "Damaged")
            self.assertNotContains(page, private_note)
            self.assertNotContains(page, private_problem)
            self.assertNotContains(page, 'data-testid="loan-return-link"')
        foreign_user = User.objects.create_user(
            username="t17_other_owner", password=None, role=UserRole.BASIC_USER
        )
        self.client.force_login(foreign_user)
        self.assertEqual(
            self.client.get(reverse("portal:loan-detail", args=[self.loan.pk])).status_code, 404
        )
        self.assertEqual(
            self.client.get(
                reverse("portal:request-detail", args=[self.loan.request_id])
            ).status_code,
            404,
        )

    def test_overdue_labels_on_admin_and_owner_pages_disappear_after_final_return(self) -> None:
        today = timezone.localdate()
        Loan.objects.filter(pk=self.loan.pk).update(
            issued_on=today - timedelta(days=3),
            issued_at=timezone.now() - timedelta(days=3),
            due_date=today - timedelta(days=2),
        )
        for user, namespace in (
            (self.records.admin, "borrowing_manage"),
            (self.records.borrower, "portal"),
        ):
            self.client.force_login(user)
            for name, args in (("loan-list", []), ("loan-detail", [self.loan.pk])):
                self.assertContains(
                    self.client.get(reverse(namespace + ":" + name, args=args)), "Overdue"
                )
        return_units(
            self.records.admin.pk,
            self.loan.pk,
            (
                ReturnInput(self.first.pk, UnitCondition.GOOD, "", ""),
                ReturnInput(self.second.pk, UnitCondition.GOOD, "", ""),
            ),
        )
        for user, namespace in (
            (self.records.admin, "borrowing_manage"),
            (self.records.borrower, "portal"),
        ):
            self.client.force_login(user)
            for name, args in (("loan-list", []), ("loan-detail", [self.loan.pk])):
                self.assertNotContains(
                    self.client.get(reverse(namespace + ":" + name, args=args)), "Overdue"
                )
