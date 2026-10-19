"""Integration test for competing administrator approvals over the last available unit (T14)."""

from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta

from django.db import connections
from django.test import TransactionTestCase
from django.utils import timezone

from accounts.models import Profile, User, UserRole
from borrowing.models import BorrowRequest, RequestItem, RequestStatus, UnitAllocation
from borrowing.services import WorkflowConflict, approve_request
from inventory.models import CatalogItem, EquipmentUnit, UnitStatus
from operations.models import AuditAction, AuditLog
from operations.tests.records import CatalogRecords, create_catalog_records


def _make_competing_request(owner: User, item: CatalogItem) -> BorrowRequest:
    today = timezone.localdate()
    due = today + timedelta(days=3)
    borrow_request = BorrowRequest.objects.create(
        owner=owner,
        purpose="Competing approval test",
        submitted_at=timezone.now(),
        submitted_on=today,
        desired_due_date=due,
        agreed_due_date=due,
        max_loan_days_applied=7,
        max_quantity_applied=3,
        status=RequestStatus.PENDING,
    )
    RequestItem.objects.create(request=borrow_request, catalog_item=item, quantity=1)
    return borrow_request


class CompetingApprovalTests(TransactionTestCase):
    """Prove competing approvals for the last unit yield exactly one winner and one conflict."""

    records: CatalogRecords
    user_two: User
    request_a: BorrowRequest
    request_b: BorrowRequest
    unit: EquipmentUnit

    def setUp(self) -> None:
        self.assertEqual(connections["default"].vendor, "postgresql")
        self.records = create_catalog_records()

        self.user_two = User.objects.create_user(
            username="competing_borrower",
            email="borrower2@example.invalid",
            password=None,
            first_name="Competing",
            last_name="Borrower",
            role=UserRole.BASIC_USER,
            is_active=True,
        )
        Profile.objects.create(user=self.user_two, contact_number="")

        # Use the single available unit from create_catalog_records
        self.unit = self.records.unit
        self.assertEqual(
            EquipmentUnit.objects.filter(
                catalog_item=self.records.item,
                status=UnitStatus.AVAILABLE,
            ).count(),
            1,
        )

        self.request_a = _make_competing_request(self.records.borrower, self.records.item)
        self.request_b = _make_competing_request(self.user_two, self.records.item)

    def test_competing_approvals_for_last_unit_allocates_atomically_to_one(self) -> None:
        admin_id = self.records.admin.pk
        req_a_id = self.request_a.pk
        req_b_id = self.request_b.pk

        def run_approval(request_id: int) -> tuple[int, BorrowRequest | None, Exception | None]:
            try:
                result = approve_request(
                    actor_id=admin_id,
                    request_id=request_id,
                    reason="Approved during competing test",
                )
                return request_id, result, None
            except Exception as exc:
                return request_id, None, exc
            finally:
                connections["default"].close()

        with ThreadPoolExecutor(max_workers=2) as executor:
            future_a = executor.submit(run_approval, req_a_id)
            future_b = executor.submit(run_approval, req_b_id)
            outcomes = [future_a.result(), future_b.result()]

        successes = [res for req_id, res, exc in outcomes if res is not None]
        failures = [exc for req_id, res, exc in outcomes if exc is not None]

        self.assertEqual(len(successes), 1)
        self.assertEqual(len(failures), 1)

        conflict = failures[0]
        self.assertIsInstance(conflict, WorkflowConflict)
        self.assertIn("Not enough available units", str(conflict))

        self.request_a.refresh_from_db()
        self.request_b.refresh_from_db()

        winning_req_id = successes[0].pk
        if self.request_a.pk == winning_req_id:
            winning_request = self.request_a
            losing_request = self.request_b
        else:
            winning_request = self.request_b
            losing_request = self.request_a

        self.assertEqual(winning_request.status, RequestStatus.APPROVED)
        self.assertEqual(
            UnitAllocation.objects.filter(request_item__request=winning_request).count(),
            1,
        )

        self.assertEqual(losing_request.status, RequestStatus.PENDING)
        self.assertEqual(
            UnitAllocation.objects.filter(request_item__request=losing_request).count(),
            0,
        )

        self.unit.refresh_from_db()
        self.assertEqual(self.unit.status, UnitStatus.RESERVED)

        allocation = UnitAllocation.objects.get(unit=self.unit)
        self.assertEqual(allocation.request_item.request_id, winning_request.pk)

        approval_audits = AuditLog.objects.filter(
            action=AuditAction.REQUEST_APPROVED,
            target_id=winning_request.pk,
        )
        self.assertEqual(approval_audits.count(), 1)
