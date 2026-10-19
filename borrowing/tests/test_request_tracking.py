"""PostgreSQL integration coverage for owner-scoped T12 request and loan tracking."""

from datetime import timedelta
from unittest.mock import patch

from django.contrib.auth import SESSION_KEY
from django.core.exceptions import PermissionDenied
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from accounts.models import User, UserRole
from borrowing.models import (
    BorrowRequest,
    Loan,
    LoanUnit,
    RequestItem,
    RequestStatus,
    ReturnRecord,
    UnitAllocation,
)
from borrowing.services import RequestCancellationConflict, cancel_request
from inventory.models import (
    EquipmentUnit,
    UnitCondition,
    UnitStatus,
)
from operations.models import AuditAction, AuditLog
from operations.tests.records import (
    CatalogRecords,
    IssuedRecords,
    create_catalog_records,
)
from operations.tests.records import create_request as create_request_item


class BorrowerRequestTrackingTests(TestCase):
    records: CatalogRecords

    @classmethod
    def setUpTestData(cls) -> None:
        cls.records = create_catalog_records()
        cls.other_borrower = User.objects.create_user(
            username="other_fictional_borrower",
            email="other-borrower@example.invalid",
            password="Test-pass-2026!",
            first_name="Other",
            last_name="Borrower",
            role=UserRole.BASIC_USER,
        )
        cls.inactive_borrower = User.objects.create_user(
            username="inactive_fictional_borrower",
            email="inactive-borrower@example.invalid",
            password="Test-pass-2026!",
            first_name="Inactive",
            last_name="Borrower",
            role=UserRole.BASIC_USER,
            is_active=False,
        )

    def setUp(self) -> None:
        self.client.force_login(self.records.borrower)

    def create_request(self, owner_id: int | None = None) -> RequestItem:
        return create_request_item(
            owner_id=owner_id or self.records.borrower.pk,
            catalog_item_id=self.records.item.pk,
            submitted_at=timezone.now() - timedelta(minutes=1),
        )

    def approve_with_reservations(
        self,
        quantity: int,
        owner_id: int | None = None,
    ) -> tuple[BorrowRequest, tuple[UnitAllocation, ...]]:
        request_item: RequestItem = self.create_request(owner_id)
        request_item.quantity = quantity
        request_item.save(update_fields=["quantity"])
        borrow_request: BorrowRequest = request_item.request
        borrow_request.status = RequestStatus.APPROVED
        borrow_request.decided_by = self.records.admin
        borrow_request.decided_at = timezone.now()
        borrow_request.decision_reason = "Fictional reservation approved."
        borrow_request.save(update_fields=["status", "decided_by", "decided_at", "decision_reason"])
        units: list[EquipmentUnit] = [self.records.unit]
        for index in range(1, quantity):
            units.append(
                EquipmentUnit.objects.create(
                    catalog_item=self.records.item,
                    asset_code=f"TEST-CAM-CANCEL-{index:03}",
                    condition=UnitCondition.GOOD,
                    acquired_on=timezone.localdate(),
                    status=UnitStatus.AVAILABLE,
                    internal_notes="",
                )
            )
        EquipmentUnit.objects.filter(pk__in=[unit.pk for unit in units]).update(
            status=UnitStatus.RESERVED
        )
        allocations: tuple[UnitAllocation, ...] = tuple(
            UnitAllocation.objects.create(
                request_item=request_item,
                unit=unit,
                allocated_at=timezone.now(),
                allocated_by=self.records.admin,
            )
            for unit in units
        )
        return borrow_request, allocations

    def create_issued_loan(self, owner_id: int | None = None) -> IssuedRecords:
        issued_at = timezone.now()
        request_item: RequestItem = self.create_request(owner_id)
        borrow_request: BorrowRequest = request_item.request
        borrow_request.status = RequestStatus.ISSUED
        borrow_request.decided_by = self.records.admin
        borrow_request.decided_at = issued_at
        borrow_request.decision_reason = "Fictional request approved."
        borrow_request.save(update_fields=["status", "decided_by", "decided_at", "decision_reason"])
        EquipmentUnit.objects.filter(pk=self.records.unit.pk).update(status=UnitStatus.ISSUED)
        allocation: UnitAllocation = UnitAllocation.objects.create(
            request_item=request_item,
            unit=self.records.unit,
            allocated_at=issued_at,
            allocated_by=self.records.admin,
            released_at=issued_at,
        )
        loan: Loan = Loan.objects.create(
            request=borrow_request,
            issued_by=self.records.admin,
            issued_at=issued_at,
            issued_on=timezone.localdate(issued_at),
            due_date=borrow_request.agreed_due_date,
        )
        loan_unit: LoanUnit = LoanUnit.objects.create(loan=loan, allocation=allocation)
        return IssuedRecords(
            catalog=self.records,
            request=borrow_request,
            request_item=request_item,
            allocation=allocation,
            loan=loan,
            loan_unit=loan_unit,
        )

    def test_request_history_filters_status_and_excludes_other_borrowers(self) -> None:
        pending_item: RequestItem = self.create_request()
        rejected_item: RequestItem = self.create_request()
        rejected_item.request.status = RequestStatus.REJECTED
        rejected_item.request.decided_by = self.records.admin
        rejected_item.request.decided_at = timezone.now()
        rejected_item.request.decision_reason = "Fictional item unavailable."
        rejected_item.request.save(
            update_fields=["status", "decided_by", "decided_at", "decision_reason"]
        )
        other_item: RequestItem = self.create_request(self.other_borrower.pk)

        response = self.client.get(reverse("portal:request-list"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["active_portal_tab"], "request-list")
        self.assertEqual(
            {row.pk for row in response.context["page"].object_list},
            {pending_item.request_id, rejected_item.request_id},
        )
        filtered = self.client.get(
            reverse("portal:request-list"), {"status": RequestStatus.REJECTED}
        )
        self.assertEqual(filtered.status_code, 200)
        self.assertEqual(
            [row.pk for row in filtered.context["page"].object_list],
            [rejected_item.request_id],
        )
        invalid_filter = self.client.get(reverse("portal:request-list"), {"status": "UNKNOWN"})
        self.assertEqual(invalid_filter.status_code, 200)
        self.assertTrue(invalid_filter.context["form"].errors)
        self.assertFalse(invalid_filter.context["page"].object_list)
        self.assertEqual(
            self.client.get(reverse("portal:request-list"), {"page": "bad"}).status_code,
            404,
        )
        self.assertNotContains(response, f"Request #{other_item.request_id}")

    def test_request_detail_is_owner_scoped_and_exposes_decision(self) -> None:
        request_item: RequestItem = self.create_request()
        borrow_request: BorrowRequest = request_item.request
        borrow_request.status = RequestStatus.REJECTED
        borrow_request.decided_by = self.records.admin
        borrow_request.decided_at = timezone.now()
        borrow_request.decision_reason = "Fictional review reason."
        borrow_request.save(update_fields=["status", "decided_by", "decided_at", "decision_reason"])
        foreign_item: RequestItem = self.create_request(self.other_borrower.pk)

        response = self.client.get(
            reverse("portal:request-detail", kwargs={"request_id": borrow_request.pk})
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["active_portal_tab"], "request-list")
        self.assertContains(response, "Fictional review reason.")
        self.assertContains(response, self.records.item.name)
        self.assertEqual(
            self.client.get(
                reverse("portal:request-detail", kwargs={"request_id": foreign_item.request_id})
            ).status_code,
            404,
        )

    def test_pending_cancellation_is_csrf_protected_and_audited(self) -> None:
        request_item: RequestItem = self.create_request()
        cancel_url: str = reverse(
            "portal:request-cancel",
            kwargs={"request_id": request_item.request_id},
        )
        csrf_client: Client = Client(enforce_csrf_checks=True)
        csrf_client.force_login(self.records.borrower)

        confirmation = csrf_client.get(cancel_url)
        self.assertEqual(confirmation.status_code, 200)
        self.assertIsNone(BorrowRequest.objects.get(pk=request_item.request_id).cancelled_at)
        self.assertEqual(csrf_client.post(cancel_url).status_code, 403)

        response = self.client.post(cancel_url)

        self.assertEqual(response.status_code, 302)
        updated: BorrowRequest = BorrowRequest.objects.get(pk=request_item.request_id)
        self.assertEqual(updated.status, RequestStatus.CANCELLED)
        self.assertEqual(updated.cancelled_by_id, self.records.borrower.pk)
        self.assertIsNotNone(updated.cancelled_at)
        self.assertEqual(
            AuditLog.objects.filter(
                action=AuditAction.REQUEST_CANCELLED,
                target_id=updated.pk,
            ).count(),
            1,
        )
        self.assertEqual(self.client.post(cancel_url).status_code, 409)
        self.assertEqual(
            AuditLog.objects.filter(
                action=AuditAction.REQUEST_CANCELLED,
                target_id=updated.pk,
            ).count(),
            1,
        )
        self.assertEqual(
            response["Location"],
            reverse("portal:request-detail", kwargs={"request_id": updated.pk}),
        )

    def test_approved_cancellation_releases_every_reserved_unit_atomically(self) -> None:
        borrow_request, allocations = self.approve_with_reservations(2)
        unit_ids: tuple[int, ...] = tuple(allocation.unit_id for allocation in allocations)

        response = self.client.post(
            reverse("portal:request-cancel", kwargs={"request_id": borrow_request.pk})
        )

        self.assertEqual(response.status_code, 302)
        borrow_request.refresh_from_db()
        self.assertEqual(borrow_request.status, RequestStatus.CANCELLED)
        self.assertEqual(
            set(EquipmentUnit.objects.filter(pk__in=unit_ids).values_list("status", flat=True)),
            {UnitStatus.AVAILABLE},
        )
        for allocation in UnitAllocation.objects.filter(pk__in=[row.pk for row in allocations]):
            self.assertIsNotNone(allocation.cancelled_at)
            self.assertEqual(allocation.cancelled_at, allocation.ended_at)
            self.assertIsNone(allocation.released_at)
        self.assertEqual(
            AuditLog.objects.filter(
                action=AuditAction.REQUEST_CANCELLED,
                target_id=borrow_request.pk,
            ).count(),
            1,
        )

    def test_cancellation_conflicts_after_issue_and_for_foreign_requests(self) -> None:
        issued = self.create_issued_loan(self.other_borrower.pk)
        foreign_request: RequestItem = self.create_request(self.other_borrower.pk)
        foreign_cancel = self.client.get(
            reverse("portal:request-cancel", kwargs={"request_id": foreign_request.request_id})
        )
        self.assertEqual(foreign_cancel.status_code, 404)
        self.assertEqual(
            self.client.post(
                reverse("portal:request-cancel", kwargs={"request_id": foreign_request.request_id})
            ).status_code,
            404,
        )

        issued.request.owner = self.records.borrower
        issued.request.save(update_fields=["owner"])
        issued.request.refresh_from_db()
        cancel_url = reverse("portal:request-cancel", kwargs={"request_id": issued.request.pk})
        self.assertEqual(self.client.get(cancel_url).status_code, 409)
        self.assertEqual(self.client.post(cancel_url).status_code, 409)
        issued.request.refresh_from_db()
        issued.allocation.refresh_from_db()
        issued.catalog.unit.refresh_from_db()
        self.assertEqual(issued.request.status, RequestStatus.ISSUED)
        self.assertIsNone(issued.allocation.cancelled_at)
        self.assertEqual(issued.catalog.unit.status, UnitStatus.ISSUED)
        self.assertFalse(
            AuditLog.objects.filter(
                action=AuditAction.REQUEST_CANCELLED,
                target_id=issued.request.pk,
            ).exists()
        )

    def test_cancel_service_rolls_back_reservations_when_audit_fails(self) -> None:
        borrow_request, allocations = self.approve_with_reservations(2)
        with patch("borrowing.services.write_audit", side_effect=RuntimeError("audit failure")):
            with self.assertRaisesRegex(RuntimeError, "audit failure"):
                cancel_request(self.records.borrower.pk, borrow_request.pk)

        borrow_request.refresh_from_db()
        self.assertEqual(borrow_request.status, RequestStatus.APPROVED)
        self.assertIsNone(borrow_request.cancelled_at)
        self.assertEqual(
            set(
                EquipmentUnit.objects.filter(
                    pk__in=[allocation.unit_id for allocation in allocations]
                ).values_list("status", flat=True)
            ),
            {UnitStatus.RESERVED},
        )
        self.assertFalse(
            UnitAllocation.objects.filter(
                pk__in=[allocation.pk for allocation in allocations],
                cancelled_at__isnull=False,
            ).exists()
        )

    def test_approved_cancellation_rejects_inconsistent_reservations_without_partial_release(
        self,
    ) -> None:
        borrow_request, allocations = self.approve_with_reservations(2)
        EquipmentUnit.objects.filter(pk=allocations[0].unit_id).update(status=UnitStatus.AVAILABLE)

        with self.assertRaises(RequestCancellationConflict):
            cancel_request(self.records.borrower.pk, borrow_request.pk)

        borrow_request.refresh_from_db()
        self.assertEqual(borrow_request.status, RequestStatus.APPROVED)
        self.assertFalse(
            UnitAllocation.objects.filter(
                pk__in=[allocation.pk for allocation in allocations],
                ended_at__isnull=False,
            ).exists()
        )
        self.assertEqual(
            EquipmentUnit.objects.get(pk=allocations[1].unit_id).status,
            UnitStatus.RESERVED,
        )
        self.assertFalse(
            AuditLog.objects.filter(
                action=AuditAction.REQUEST_CANCELLED,
                target_id=borrow_request.pk,
            ).exists()
        )

    def test_cancel_service_rechecks_active_basic_user_and_state(self) -> None:
        pending_item: RequestItem = self.create_request()
        with self.assertRaises(BorrowRequest.DoesNotExist):
            cancel_request(self.records.admin.pk, pending_item.request_id)
        User.objects.filter(pk=self.records.borrower.pk).update(role=UserRole.ADMIN)
        with self.assertRaises(PermissionDenied):
            cancel_request(self.records.borrower.pk, pending_item.request_id)
        User.objects.filter(pk=self.records.borrower.pk).update(role=UserRole.BASIC_USER)
        pending_item.request.refresh_from_db()
        self.assertEqual(pending_item.request.status, RequestStatus.PENDING)

    def test_loan_history_and_detail_show_owned_unit_return_progress(self) -> None:
        issued = self.create_issued_loan(self.other_borrower.pk)
        foreign_detail_url = reverse("portal:loan-detail", kwargs={"loan_id": issued.loan.pk})
        self.assertEqual(self.client.get(foreign_detail_url).status_code, 404)
        issued.request.owner = self.records.borrower
        issued.request.save(update_fields=["owner"])
        issued.catalog.unit.asset_code = "FICTIONAL-ISSUED-001"
        issued.catalog.unit.save(update_fields=["asset_code"])

        response = self.client.get(reverse("portal:loan-list"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["active_portal_tab"], "loan-list")
        self.assertEqual(
            [loan.pk for loan in response.context["page"].object_list], [issued.loan.pk]
        )
        self.assertContains(response, issued.loan.due_date.strftime("%b"))

        detail_url = reverse("portal:loan-detail", kwargs={"loan_id": issued.loan.pk})
        detail = self.client.get(detail_url)
        self.assertEqual(detail.status_code, 200)
        self.assertEqual(detail.context["active_portal_tab"], "loan-list")
        self.assertContains(detail, "FICTIONAL-ISSUED-001")
        self.assertContains(detail, "Awaiting return")
        request_detail = self.client.get(
            reverse("portal:request-detail", kwargs={"request_id": issued.request.pk})
        )
        self.assertEqual(request_detail.status_code, 200)
        self.assertContains(request_detail, "FICTIONAL-ISSUED-001")
        self.assertContains(request_detail, "Not yet returned")

        ReturnRecord.objects.create(
            loan_unit=issued.loan_unit,
            returned_at=timezone.now(),
            returned_condition=UnitCondition.FAIR,
            received_by=self.records.admin,
            notes="Fictional return notes are not shown to borrowers.",
        )
        returned_detail = self.client.get(detail_url)
        self.assertEqual(returned_detail.status_code, 200)
        self.assertContains(returned_detail, "Condition: Fair")
        self.assertNotContains(returned_detail, "Fictional return notes")
        returned_request_detail = self.client.get(
            reverse("portal:request-detail", kwargs={"request_id": issued.request.pk})
        )
        self.assertEqual(returned_request_detail.status_code, 200)
        self.assertContains(returned_request_detail, "Condition: Fair")

    def test_portal_access_and_methods_remain_restricted(self) -> None:
        request_path: str = reverse("portal:request-list")
        loan_path: str = reverse("portal:loan-list")
        self.assertEqual(self.client.post(request_path).status_code, 405)
        self.assertEqual(self.client.post(loan_path).status_code, 405)

        anonymous: Client = Client()
        self.assertEqual(anonymous.get(request_path).status_code, 302)
        self.client.force_login(self.records.admin)
        self.assertEqual(self.client.get(request_path).status_code, 403)
        self.assertEqual(self.client.get(loan_path).status_code, 403)
        self.client.force_login(self.inactive_borrower)
        self.assertEqual(self.client.get(request_path).status_code, 403)
        self.assertNotIn(SESSION_KEY, self.client.session)
        self.client.force_login(self.other_borrower)
        self.assertEqual(self.client.get(request_path).status_code, 200)
