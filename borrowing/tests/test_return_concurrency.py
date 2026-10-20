"""T17 overlapping PostgreSQL returns, using distinct receiving administrators."""

from concurrent.futures import Future, ThreadPoolExecutor
from queue import Queue
from typing import Literal

from django.db import connection, connections, transaction
from django.test import TransactionTestCase

from accounts.models import User, UserRole
from borrowing.models import Loan, LoanUnit, RequestStatus, ReturnRecord, UnitAllocation
from borrowing.return_services import ReturnInput, return_units
from borrowing.services import WorkflowConflict
from borrowing.tests.test_approval_concurrency import wait_for_blocked_approvals
from borrowing.tests.test_release_concurrency import prepare_connection
from borrowing.tests.test_returns import create_return_loan
from inventory.models import MaintenanceRecord, UnitCondition, UnitStatus
from operations.models import AuditAction, AuditLog
from operations.tests.records import CatalogRecords, create_catalog_records

ReturnOutcome = Literal["returned", "conflict"]


def competing_return(
    actor_id: int, loan_id: int, loan_unit_id: int, backend_pids: Queue[int]
) -> ReturnOutcome:
    try:
        prepare_connection(backend_pids)
        try:
            return_units(
                actor_id,
                loan_id,
                (
                    ReturnInput(
                        loan_unit_id, UnitCondition.DAMAGED, "Race inspection", "Cracked case"
                    ),
                ),
            )
        except WorkflowConflict:
            return "conflict"
        return "returned"
    finally:
        connections["default"].close()


class ReturnConcurrencyTests(TransactionTestCase):
    records: CatalogRecords
    loan: Loan
    first: LoanUnit
    second: LoanUnit
    second_admin: User

    def setUp(self) -> None:
        self.assertEqual(connection.vendor, "postgresql")
        self.records = create_catalog_records()
        self.loan = create_return_loan(self.records)
        self.first, self.second = tuple(self.loan.units.order_by("pk"))
        self.second_admin = User.objects.create_user(
            username="t17_second_admin", password=None, role=UserRole.ADMIN
        )

    def run_returns(
        self, first_unit_id: int, second_unit_id: int
    ) -> tuple[ReturnOutcome, ReturnOutcome]:
        backend_pids: Queue[int] = Queue()
        with ThreadPoolExecutor(max_workers=2) as executor:
            with transaction.atomic():
                User.objects.select_for_update().get(pk=self.records.borrower.pk)
                with connection.cursor() as cursor:
                    cursor.execute("SELECT pg_backend_pid()")
                    blocker_pid: int = cursor.fetchone()[0]
                first: Future[ReturnOutcome] = executor.submit(
                    competing_return,
                    self.records.admin.pk,
                    self.loan.pk,
                    first_unit_id,
                    backend_pids,
                )
                second: Future[ReturnOutcome] = executor.submit(
                    competing_return,
                    self.second_admin.pk,
                    self.loan.pk,
                    second_unit_id,
                    backend_pids,
                )
                worker_pids: tuple[int, int] = (
                    backend_pids.get(timeout=5),
                    backend_pids.get(timeout=5),
                )
                self.assertEqual(len({blocker_pid, *worker_pids}), 3)
                wait_for_blocked_approvals(blocker_pid, worker_pids)
            return first.result(timeout=20), second.result(timeout=20)

    def test_duplicate_return_has_one_record_maintenance_and_audit_pair(self) -> None:
        self.assertCountEqual(
            self.run_returns(self.first.pk, self.first.pk), ("returned", "conflict")
        )
        self.assertEqual(ReturnRecord.objects.count(), 1)
        self.assertEqual(MaintenanceRecord.objects.count(), 1)
        self.assertEqual(AuditLog.objects.filter(action=AuditAction.UNIT_RETURNED).count(), 1)
        self.assertEqual(AuditLog.objects.filter(action=AuditAction.MAINTENANCE_OPENED).count(), 1)
        self.loan.refresh_from_db()
        self.loan.request.refresh_from_db()
        self.assertIsNone(self.loan.closed_at)
        self.assertEqual(self.loan.request.status, RequestStatus.PARTIALLY_RETURNED)
        self.assertEqual(UnitAllocation.objects.filter(ended_at__isnull=True).count(), 1)
        self.assertEqual(self.second.allocation.unit.status, UnitStatus.ISSUED)

    def test_disjoint_partial_returns_serialize_and_close_after_both(self) -> None:
        self.assertEqual(self.run_returns(self.first.pk, self.second.pk), ("returned", "returned"))
        self.assertEqual(ReturnRecord.objects.count(), 2)
        self.assertEqual(MaintenanceRecord.objects.count(), 2)
        self.assertEqual(AuditLog.objects.filter(action=AuditAction.UNIT_RETURNED).count(), 2)
        self.assertEqual(AuditLog.objects.filter(action=AuditAction.MAINTENANCE_OPENED).count(), 2)
        self.loan.refresh_from_db()
        self.loan.request.refresh_from_db()
        self.assertEqual(
            self.loan.closed_at, ReturnRecord.objects.latest("returned_at").returned_at
        )
        self.assertEqual(self.loan.request.status, RequestStatus.RETURNED)
        self.assertFalse(UnitAllocation.objects.filter(ended_at__isnull=True).exists())
