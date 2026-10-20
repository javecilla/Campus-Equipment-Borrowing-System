"""T15 real PostgreSQL service and HTTP checks, including audit rollback."""

from datetime import date, timedelta

from django.core.exceptions import PermissionDenied, ValidationError
from django.db import IntegrityError, connection, transaction
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from accounts.models import User
from borrowing.models import BorrowRequest, Loan, LoanUnit, RequestStatus, UnitAllocation
from borrowing.queries import manage_loan_history
from borrowing.release_services import release_request, revise_due_date
from borrowing.services import (
    RequestCancellationConflict,
    WorkflowConflict,
    approve_request,
    cancel_request,
)
from inventory.models import CatalogItem, EquipmentUnit, UnitStatus
from operations.models import AuditAction, AuditLog, SystemSetting
from operations.tests.records import CatalogRecords, create_catalog_records, create_request


class ReleaseTestBase(TestCase):
    records: CatalogRecords
    borrow_request: BorrowRequest
    original_due: date

    @classmethod
    def setUpTestData(cls) -> None:
        cls.records = create_catalog_records()
        EquipmentUnit.objects.create(
            catalog_item=cls.records.item,
            asset_code="T15-CAM-002",
            condition=cls.records.unit.condition,
            acquired_on=timezone.localdate(),
            status=UnitStatus.AVAILABLE,
        )
        line = create_request(cls.records.borrower.pk, cls.records.item.pk, timezone.now())
        line.quantity = 2
        line.save(update_fields=["quantity"])
        cls.borrow_request = approve_request(cls.records.admin.pk, line.request_id, "T15 approval")
        cls.original_due = cls.borrow_request.desired_due_date

    def assert_reserved(self) -> None:
        self.borrow_request.refresh_from_db()
        self.assertEqual(self.borrow_request.status, RequestStatus.APPROVED)
        self.assertFalse(Loan.objects.exists())
        self.assertFalse(LoanUnit.objects.exists())
        self.assertFalse(UnitAllocation.objects.filter(released_at__isnull=False).exists())
        self.assertEqual(EquipmentUnit.objects.filter(status=UnitStatus.RESERVED).count(), 2)
        self.assertFalse(AuditLog.objects.filter(action=AuditAction.LOAN_RELEASED).exists())


class ReleaseServiceTests(ReleaseTestBase):
    def test_release_issues_every_unit_once_and_keeps_exclusivity(self) -> None:
        loan: Loan = release_request(self.records.admin.pk, self.borrow_request.pk)
        self.borrow_request.refresh_from_db()
        self.assertEqual(self.borrow_request.status, RequestStatus.ISSUED)
        self.assertEqual(self.borrow_request.decision_reason, "T15 approval")
        self.assertEqual(loan.request_id, self.borrow_request.pk)
        self.assertEqual(loan.issued_by_id, self.records.admin.pk)
        self.assertEqual(loan.issued_on, timezone.localdate(loan.issued_at))
        self.assertEqual(loan.due_date, self.original_due)
        self.assertEqual(loan.units.count(), 2)
        self.assertEqual(EquipmentUnit.objects.filter(status=UnitStatus.ISSUED).count(), 2)
        for allocation in UnitAllocation.objects.all():
            self.assertEqual(allocation.released_at, loan.issued_at)
            self.assertIsNone(allocation.ended_at)
            self.assertIsNone(allocation.cancelled_at)
            self.assertEqual(allocation.loan_unit.loan_id, loan.pk)
        audit: AuditLog = AuditLog.objects.get(action=AuditAction.LOAN_RELEASED)
        self.assertEqual(audit.target_id, loan.pk)
        self.assertEqual(audit.actor_id, self.records.admin.pk)
        with self.assertRaises(WorkflowConflict):
            release_request(self.records.admin.pk, self.borrow_request.pk)
        with self.assertRaises(WorkflowConflict):
            revise_due_date(
                self.records.admin.pk, self.borrow_request.pk, self.original_due, "Late"
            )
        with self.assertRaises(RequestCancellationConflict):
            cancel_request(self.records.borrower.pk, self.borrow_request.pk)
        self.assertEqual(Loan.objects.count(), 1)
        with self.assertRaises(IntegrityError), transaction.atomic():
            UnitAllocation.objects.create(
                request_item=create_request(
                    self.records.borrower.pk, self.records.item.pk, timezone.now()
                ),
                unit=self.records.unit,
                allocated_at=timezone.now(),
                allocated_by=self.records.admin,
            )

    def test_due_date_revision_preserves_request_and_uses_snapshotted_limits(self) -> None:
        SystemSetting.objects.filter(pk=1).update(max_loan_days=1)
        new_due: date = self.borrow_request.submitted_on + timedelta(days=7)
        revised = revise_due_date(
            self.records.admin.pk, self.borrow_request.pk, new_due, "Class moved"
        )
        self.assertEqual(revised.agreed_due_date, new_due)
        self.assertEqual(revised.desired_due_date, self.original_due)
        self.assertEqual(revised.max_loan_days_applied, 7)
        audit = AuditLog.objects.get(action=AuditAction.DUE_DATE_REVISED)
        self.assertEqual(audit.target_id, revised.pk)
        self.assertIn(self.original_due.isoformat(), audit.summary)
        self.assertIn(new_due.isoformat(), audit.summary)
        self.assertIn("Class moved", audit.summary)
        loan = release_request(self.records.admin.pk, revised.pk)
        self.assertEqual(loan.due_date, new_due)

    def test_invalid_dates_reasons_and_noop_revision_change_nothing(self) -> None:
        today: date = timezone.localdate()
        cases: tuple[tuple[date, str], ...] = (
            (today, "Submission date"),
            (today - timedelta(days=1), "Past date"),
            (today + timedelta(days=8), "Exceeds snapshot"),
            (self.original_due, "Unchanged"),
            (today + timedelta(days=2), "  "),
            (today + timedelta(days=2), "x" * 501),
        )
        for proposed, reason in cases:
            with self.subTest(proposed=proposed, reason_length=len(reason)):
                with self.assertRaises(ValidationError):
                    revise_due_date(self.records.admin.pk, self.borrow_request.pk, proposed, reason)
        self.borrow_request.refresh_from_db()
        self.assertEqual(self.borrow_request.agreed_due_date, self.original_due)
        self.assertFalse(AuditLog.objects.filter(action=AuditAction.DUE_DATE_REVISED).exists())
        self.assert_reserved()

    def test_expired_request_cannot_release_or_extend_beyond_snapshot(self) -> None:
        today: date = timezone.localdate()
        BorrowRequest.objects.filter(pk=self.borrow_request.pk).update(
            submitted_on=today - timedelta(days=8),
            submitted_at=timezone.now() - timedelta(days=8),
            desired_due_date=today - timedelta(days=1),
            agreed_due_date=today - timedelta(days=1),
        )
        with self.assertRaises(WorkflowConflict):
            release_request(self.records.admin.pk, self.borrow_request.pk)
        with self.assertRaises(ValidationError):
            revise_due_date(self.records.admin.pk, self.borrow_request.pk, today, "Expired limit")
        self.assert_reserved()

    def test_revision_and_release_on_today_are_allowed(self) -> None:
        BorrowRequest.objects.filter(pk=self.borrow_request.pk).update(
            submitted_on=timezone.localdate() - timedelta(days=1),
            submitted_at=timezone.now() - timedelta(days=1),
        )
        revise_due_date(
            self.records.admin.pk, self.borrow_request.pk, timezone.localdate(), "Today"
        )
        loan = release_request(self.records.admin.pk, self.borrow_request.pk)
        self.assertEqual(loan.due_date, loan.issued_on)

    def test_nonapproved_and_existing_loan_states_are_rejected(self) -> None:
        for status in RequestStatus.values:
            if status == RequestStatus.APPROVED:
                continue
            with self.subTest(status=status):
                BorrowRequest.objects.filter(pk=self.borrow_request.pk).update(status=status)
                with self.assertRaises(WorkflowConflict):
                    release_request(self.records.admin.pk, self.borrow_request.pk)
                with self.assertRaises(WorkflowConflict):
                    revise_due_date(
                        self.records.admin.pk, self.borrow_request.pk, self.original_due, "Try"
                    )
        BorrowRequest.objects.filter(pk=self.borrow_request.pk).update(
            status=RequestStatus.APPROVED
        )
        Loan.objects.create(
            request=self.borrow_request,
            issued_by=self.records.admin,
            issued_at=timezone.now(),
            issued_on=timezone.localdate(),
            due_date=self.original_due,
        )
        with self.assertRaises(WorkflowConflict):
            release_request(self.records.admin.pk, self.borrow_request.pk)
        self.assertEqual(LoanUnit.objects.count(), 0)

    def test_archived_catalog_does_not_strand_existing_reservations(self) -> None:
        CatalogItem.objects.filter(pk=self.records.item.pk).update(is_archived=True)
        self.records.category.is_archived = True
        self.records.category.save(update_fields=["is_archived"])
        self.assertEqual(
            release_request(self.records.admin.pk, self.borrow_request.pk).units.count(), 2
        )

    def test_missing_extra_or_ended_reservations_cannot_release(self) -> None:
        allocation = UnitAllocation.objects.order_by("pk").first()
        self.assertIsNotNone(allocation)
        line = allocation.request_item
        for quantity in (1, 3):
            line.quantity = quantity
            line.save(update_fields=["quantity"])
            with self.assertRaises(WorkflowConflict):
                release_request(self.records.admin.pk, self.borrow_request.pk)
        line.quantity = 2
        line.save(update_fields=["quantity"])
        for field in ("released_at", "ended_at"):
            with self.subTest(field=field):
                UnitAllocation.objects.filter(pk=allocation.pk).update(**{field: timezone.now()})
                with self.assertRaises(WorkflowConflict):
                    release_request(self.records.admin.pk, self.borrow_request.pk)
                UnitAllocation.objects.filter(pk=allocation.pk).update(**{field: None})
        self.assert_reserved()

    def test_changed_unit_item_and_status_cannot_release(self) -> None:
        unit = self.records.unit
        for status in (
            UnitStatus.AVAILABLE,
            UnitStatus.ISSUED,
            UnitStatus.MAINTENANCE,
            UnitStatus.RETIRED,
        ):
            EquipmentUnit.objects.filter(pk=unit.pk).update(status=status)
            with self.subTest(status=status), self.assertRaises(WorkflowConflict):
                release_request(self.records.admin.pk, self.borrow_request.pk)
        other = CatalogItem.objects.create(
            category=self.records.category, name="Other", description="Other item"
        )
        EquipmentUnit.objects.filter(pk=unit.pk).update(
            status=UnitStatus.RESERVED, catalog_item=other
        )
        with self.assertRaises(WorkflowConflict):
            release_request(self.records.admin.pk, self.borrow_request.pk)
        EquipmentUnit.objects.filter(pk=unit.pk).update(catalog_item=self.records.item)
        self.assert_reserved()

    def test_services_recheck_actor_and_borrower_authority(self) -> None:
        for actor_id in (self.records.borrower.pk, self.records.admin.pk):
            if actor_id == self.records.admin.pk:
                User.objects.filter(pk=actor_id).update(is_active=False)
            with self.subTest(actor=actor_id):
                with self.assertRaises(PermissionDenied):
                    release_request(actor_id, self.borrow_request.pk)
                with self.assertRaises(PermissionDenied):
                    revise_due_date(actor_id, self.borrow_request.pk, self.original_due, "Try")
        User.objects.filter(pk=self.records.admin.pk).update(is_active=True)
        User.objects.filter(pk=self.records.borrower.pk).update(is_active=False)
        with self.assertRaises(WorkflowConflict):
            release_request(self.records.admin.pk, self.borrow_request.pk)
        self.assert_reserved()

    def test_release_audit_failure_rolls_back_every_business_write(self) -> None:
        with connection.cursor() as cursor:
            cursor.execute("SET CONSTRAINTS ALL IMMEDIATE")
            cursor.execute(
                "ALTER TABLE operations_auditlog ADD CONSTRAINT test_t15_release_audit CHECK (action <> 'LOAN_RELEASED')"
            )
        with self.assertRaises(IntegrityError):
            release_request(self.records.admin.pk, self.borrow_request.pk)
        self.assert_reserved()

    def test_revision_audit_failure_preserves_original_dates(self) -> None:
        with connection.cursor() as cursor:
            cursor.execute("SET CONSTRAINTS ALL IMMEDIATE")
            cursor.execute(
                "ALTER TABLE operations_auditlog ADD CONSTRAINT test_t15_revision_audit CHECK (action <> 'DUE_DATE_REVISED')"
            )
        with self.assertRaises(IntegrityError):
            revise_due_date(
                self.records.admin.pk,
                self.borrow_request.pk,
                self.original_due + timedelta(days=1),
                "Rollback",
            )
        self.borrow_request.refresh_from_db()
        self.assertEqual(self.borrow_request.agreed_due_date, self.original_due)
        self.assertEqual(self.borrow_request.desired_due_date, self.original_due)
        self.assert_reserved()


class ReleaseHttpTests(ReleaseTestBase):
    def test_end_to_end_revision_release_detail_and_print_ignore_forged_fields(self) -> None:
        self.client.force_login(self.records.admin)
        due_url = reverse("borrowing_manage:request-due-date", args=[self.borrow_request.pk])
        release_url = reverse("borrowing_manage:request-release", args=[self.borrow_request.pk])
        self.assertEqual(self.client.get(due_url).status_code, 200)
        self.assertEqual(self.client.get(release_url).status_code, 200)
        self.assert_reserved()
        revised_date: date = self.original_due + timedelta(days=1)
        response = self.client.post(
            due_url,
            {
                "agreed_due_date": revised_date.isoformat(),
                "reason": "Changed class date",
                "desired_due_date": "2099-01-01",
                "max_loan_days_applied": "999",
            },
        )
        self.assertRedirects(
            response, reverse("borrowing_manage:request-detail", args=[self.borrow_request.pk])
        )
        response = self.client.post(
            release_url,
            {
                "issued_by": self.records.borrower.pk,
                "due_date": "2099-01-01",
                "status": "RETURNED",
                "unit": "99999",
            },
        )
        loan = Loan.objects.get(request=self.borrow_request)
        self.assertRedirects(response, reverse("borrowing_manage:loan-detail", args=[loan.pk]))
        self.assertEqual(loan.issued_by_id, self.records.admin.pk)
        self.assertEqual(loan.due_date, revised_date)
        self.borrow_request.refresh_from_db()
        self.assertEqual(self.borrow_request.desired_due_date, self.original_due)
        for name in ("loan-detail", "loan-slip"):
            page = self.client.get(reverse("borrowing_manage:" + name, args=[loan.pk]))
            self.assertContains(page, self.records.borrower.username)
            self.assertContains(page, "TEST-CAM-001")
            self.assertContains(page, "T15-CAM-002")
            self.assertContains(page, revised_date.strftime("%b"))
        self.assertEqual(self.client.post(release_url).status_code, 409)
        self.assertEqual(self.client.get(due_url).status_code, 409)
        self.assertEqual(Loan.objects.count(), 1)

    def test_invalid_date_and_reason_return_bound_errors_without_writes(self) -> None:
        self.client.force_login(self.records.admin)
        url = reverse("borrowing_manage:request-due-date", args=[self.borrow_request.pk])
        for values in (
            {"agreed_due_date": "invalid", "reason": "Try"},
            {"agreed_due_date": "2099-01-01", "reason": "Try"},
            {"agreed_due_date": self.original_due.isoformat(), "reason": "   "},
        ):
            response = self.client.post(url, values)
            self.assertEqual(response.status_code, 200)
            self.assertTrue(response.context["form"].errors)
        self.assert_reserved()

    def test_print_and_all_new_routes_enforce_active_admin_methods_and_csrf(self) -> None:
        loan = release_request(self.records.admin.pk, self.borrow_request.pk)
        urls: tuple[str, ...] = (
            reverse("borrowing_manage:request-due-date", args=[self.borrow_request.pk]),
            reverse("borrowing_manage:request-release", args=[self.borrow_request.pk]),
            reverse("borrowing_manage:loan-list"),
            reverse("borrowing_manage:loan-detail", args=[loan.pk]),
            reverse("borrowing_manage:loan-slip", args=[loan.pk]),
        )
        for url in urls:
            with self.subTest(url=url):
                self.client.logout()
                self.assertEqual(self.client.get(url).status_code, 302)
                self.client.force_login(self.records.borrower)
                self.assertEqual(self.client.get(url).status_code, 403)
                self.client.force_login(self.records.admin)
                User.objects.filter(pk=self.records.admin.pk).update(is_active=False)
                self.assertEqual(self.client.get(url).status_code, 403)
                User.objects.filter(pk=self.records.admin.pk).update(is_active=True)
                self.client.force_login(self.records.admin)
                self.assertEqual(self.client.put(url).status_code, 405)
        secure = Client(enforce_csrf_checks=True)
        secure.force_login(self.records.admin)
        for url in urls[:2]:
            self.assertEqual(secure.post(url, {"reason": "No token"}).status_code, 403)
        for url in urls[2:]:
            self.assertEqual(self.client.post(url).status_code, 405)
        self.assertEqual(
            self.client.get(
                reverse("borrowing_manage:loan-slip", args=[loan.pk + 999])
            ).status_code,
            404,
        )

    def test_expired_release_returns_conflict_without_a_loan(self) -> None:
        self.client.force_login(self.records.admin)
        BorrowRequest.objects.filter(pk=self.borrow_request.pk).update(
            submitted_on=timezone.localdate() - timedelta(days=5),
            desired_due_date=timezone.localdate() - timedelta(days=1),
            agreed_due_date=timezone.localdate() - timedelta(days=1),
        )
        response = self.client.post(
            reverse("borrowing_manage:request-release", args=[self.borrow_request.pk])
        )
        self.assertEqual(response.status_code, 409)
        self.assert_reserved()

    def test_list_search_counts_and_invalid_pages(self) -> None:
        loan = release_request(self.records.admin.pk, self.borrow_request.pk)
        self.client.force_login(self.records.admin)
        url = reverse("borrowing_manage:loan-list")
        for query in (str(loan.pk), self.records.borrower.username):
            response = self.client.get(url, {"q": query})
            self.assertEqual(response.status_code, 200)
            self.assertEqual(list(response.context["page"]), [loan])
        counted = manage_loan_history("").get(pk=loan.pk)
        self.assertEqual(counted.issued_quantity, 2)
        self.assertEqual(counted.returned_quantity, 0)
        self.assertEqual(counted.outstanding_quantity, 2)
        self.assertFalse(manage_loan_history("²").exists())
        invalid = self.client.get(url, {"q": "x" * 151})
        self.assertTrue(invalid.context["form"].errors)
        self.assertEqual(list(invalid.context["page"]), [])
        for page in ("0", "bad", "2"):
            self.assertEqual(self.client.get(url, {"page": page}).status_code, 404)
