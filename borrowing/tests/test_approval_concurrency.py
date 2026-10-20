"""T14: competing approval transactions against committed PostgreSQL records."""

from concurrent.futures import Future, ThreadPoolExecutor
from dataclasses import dataclass
from queue import Queue
from time import monotonic, sleep
from typing import Literal

from django.db import connection, connections, transaction
from django.test import TransactionTestCase
from django.utils import timezone

from accounts.models import User, UserRole
from borrowing.models import BorrowRequest, Loan, RequestItem, RequestStatus, UnitAllocation
from borrowing.services import WorkflowConflict, approve_request
from inventory.models import CatalogItem, Category, EquipmentUnit, UnitCondition, UnitStatus
from operations.models import AuditAction, AuditLog, AuditTarget
from operations.tests.records import CatalogRecords, create_catalog_records, create_request


@dataclass(frozen=True)
class ApprovalResult:
    request_id: int
    actor_id: int
    backend_pid: int
    outcome: Literal["approved", "conflict"]
    conflict_message: str


def competing_approval(actor_id: int, request_id: int, backend_pids: Queue[int]) -> ApprovalResult:
    """Use one thread-local connection; only the domain conflict is an expected loser."""
    try:
        with connections["default"].cursor() as cursor:
            cursor.execute("SET lock_timeout = '10s'")
            cursor.execute("SET statement_timeout = '15s'")
            cursor.execute("SELECT pg_backend_pid()")
            backend_pid: int = cursor.fetchone()[0]
        backend_pids.put(backend_pid)
        try:
            approve_request(
                actor_id, request_id, f"T14 competing approval for request {request_id}"
            )
        except WorkflowConflict as error:
            return ApprovalResult(
                request_id=request_id,
                actor_id=actor_id,
                backend_pid=backend_pid,
                outcome="conflict",
                conflict_message=str(error),
            )
        return ApprovalResult(
            request_id=request_id,
            actor_id=actor_id,
            backend_pid=backend_pid,
            outcome="approved",
            conflict_message="",
        )
    finally:
        connections["default"].close()


def wait_for_blocked_approvals(blocker_pid: int, backend_pids: tuple[int, int]) -> None:
    """Require both transactions to wait, including PostgreSQL's queued-lock blockers."""
    deadline: float = monotonic() + 5
    blocked: set[int] = set()
    while monotonic() < deadline:
        with connection.cursor() as cursor:
            cursor.execute(
                "WITH RECURSIVE waits(root, pid) AS ("
                "SELECT pid, pid FROM unnest(%s::integer[]) AS pid "
                "UNION SELECT waits.root, blockers.pid FROM waits "
                "CROSS JOIN LATERAL unnest(pg_blocking_pids(waits.pid)) AS blockers(pid)"
                ") SELECT root FROM waits WHERE pid = %s",
                [list(backend_pids), blocker_pid],
            )
            blocked = {row[0] for row in cursor.fetchall()}
        if blocked == set(backend_pids):
            return
        sleep(0.01)
    raise AssertionError(
        f"Both approval connections {backend_pids} must block on connection {blocker_pid}; "
        f"observed blocked connections: {sorted(blocked)}."
    )


class ApprovalConcurrencyTests(TransactionTestCase):
    records: CatalogRecords
    second_admin: User
    first_request: BorrowRequest
    second_request: BorrowRequest

    def setUp(self) -> None:
        self.assertEqual(connection.vendor, "postgresql")
        self.records = create_catalog_records()
        self.second_admin = User.objects.create_user(
            username="t14_second_admin", password=None, role=UserRole.ADMIN
        )
        second_borrower: User = User.objects.create_user(
            username="t14_second_borrower", password=None, role=UserRole.BASIC_USER
        )
        self.first_request = create_request(
            self.records.borrower.pk, self.records.item.pk, timezone.now()
        ).request
        self.second_request = create_request(
            second_borrower.pk, self.records.item.pk, timezone.now()
        ).request

    def compete_for_last_unit(self) -> tuple[ApprovalResult, ApprovalResult]:
        """Distinct borrowers/admins prevent account/request locks from serializing the race."""
        backend_pids: Queue[int] = Queue()
        with ThreadPoolExecutor(max_workers=2) as executor:
            with transaction.atomic():
                Category.objects.select_for_update().get(pk=self.records.category.pk)
                with connection.cursor() as cursor:
                    cursor.execute("SELECT pg_backend_pid()")
                    blocker_pid: int = cursor.fetchone()[0]
                first: Future[ApprovalResult] = executor.submit(
                    competing_approval, self.records.admin.pk, self.first_request.pk, backend_pids
                )
                second: Future[ApprovalResult] = executor.submit(
                    competing_approval, self.second_admin.pk, self.second_request.pk, backend_pids
                )
                worker_pids: tuple[int, int] = (
                    backend_pids.get(timeout=5),
                    backend_pids.get(timeout=5),
                )
                self.assertEqual(len({blocker_pid, *worker_pids}), 3)
                wait_for_blocked_approvals(blocker_pid, worker_pids)
            results: tuple[ApprovalResult, ApprovalResult] = (
                first.result(timeout=20),
                second.result(timeout=20),
            )
        self.assertEqual({result.backend_pid for result in results}, set(worker_pids))
        self.assertCountEqual([result.outcome for result in results], ["approved", "conflict"])
        winner: ApprovalResult = next(result for result in results if result.outcome == "approved")
        loser: ApprovalResult = next(result for result in results if result.outcome == "conflict")
        return winner, loser

    def assert_complete_decision(self, winner: ApprovalResult, loser: ApprovalResult) -> None:
        approved: BorrowRequest = BorrowRequest.objects.get(pk=winner.request_id)
        pending: BorrowRequest = BorrowRequest.objects.get(pk=loser.request_id)
        self.assertEqual(approved.status, RequestStatus.APPROVED)
        self.assertEqual(approved.decided_by_id, winner.actor_id)
        self.assertIsNotNone(approved.decided_at)
        self.assertEqual(
            approved.decision_reason, f"T14 competing approval for request {winner.request_id}"
        )
        self.assertIn("Nothing was reserved", loser.conflict_message)
        self.assertEqual(pending.status, RequestStatus.PENDING)
        self.assertIsNone(pending.decided_by_id)
        self.assertIsNone(pending.decided_at)
        self.assertEqual(pending.decision_reason, "")
        self.assertFalse(UnitAllocation.objects.filter(request_item__request=pending).exists())
        self.assertEqual(
            list(
                AuditLog.objects.filter(
                    target_model=AuditTarget.BORROW_REQUEST,
                    target_id__in=(winner.request_id, loser.request_id),
                ).values_list("action", "target_id", "actor_id")
            ),
            [(AuditAction.REQUEST_APPROVED, winner.request_id, winner.actor_id)],
        )
        self.assertEqual(Loan.objects.count(), 0)
        self.records.unit.refresh_from_db()
        self.assertEqual(self.records.unit.status, UnitStatus.RESERVED)
        allocation: UnitAllocation = UnitAllocation.objects.get(unit=self.records.unit)
        self.assertEqual(allocation.request_item.request_id, winner.request_id)
        self.assertEqual(allocation.allocated_by_id, winner.actor_id)
        self.assertEqual(allocation.allocated_at, approved.decided_at)
        self.assertIsNone(allocation.ended_at)
        self.assertIsNone(allocation.released_at)
        self.assertIsNone(allocation.cancelled_at)

    def test_last_unit_has_one_approval_and_one_workflow_conflict(self) -> None:
        winner, loser = self.compete_for_last_unit()

        self.assert_complete_decision(winner, loser)
        self.assertEqual(UnitAllocation.objects.count(), 1)
        self.assertEqual(EquipmentUnit.objects.filter(status=UnitStatus.RESERVED).count(), 1)
        self.assertEqual(EquipmentUnit.objects.filter(status=UnitStatus.AVAILABLE).count(), 0)

    def test_multi_item_loser_keeps_other_stock_available_without_partial_allocations(self) -> None:
        # Each request has an uncontested item before its shared, last-unit item.
        extra_units: tuple[EquipmentUnit, ...] = tuple(
            EquipmentUnit.objects.create(
                catalog_item=CatalogItem.objects.create(
                    category=self.records.category,
                    name=f"T14 extra item {request.pk}",
                    description="Uncontested stock for the multi-item approval race.",
                ),
                asset_code=f"T14-EXTRA-{request.pk}",
                condition=UnitCondition.GOOD,
                acquired_on=timezone.localdate(),
                status=UnitStatus.AVAILABLE,
            )
            for request in (self.first_request, self.second_request)
        )
        for request, unit in zip(
            (self.first_request, self.second_request), extra_units, strict=True
        ):
            request.items.all().delete()
            RequestItem.objects.create(request=request, catalog_item=unit.catalog_item, quantity=1)
            RequestItem.objects.create(request=request, catalog_item=self.records.item, quantity=1)

        winner, loser = self.compete_for_last_unit()

        self.assert_complete_decision(winner, loser)
        for request, unit in zip(
            (self.first_request, self.second_request), extra_units, strict=True
        ):
            unit.refresh_from_db()
            if request.pk == winner.request_id:
                self.assertEqual(unit.status, UnitStatus.RESERVED)
                self.assertEqual(
                    UnitAllocation.objects.get(unit=unit).request_item.request_id, winner.request_id
                )
            else:
                self.assertEqual(unit.status, UnitStatus.AVAILABLE)
                self.assertFalse(UnitAllocation.objects.filter(unit=unit).exists())
        self.assertEqual(UnitAllocation.objects.count(), 2)
        self.assertEqual(EquipmentUnit.objects.filter(status=UnitStatus.RESERVED).count(), 2)
        self.assertEqual(EquipmentUnit.objects.filter(status=UnitStatus.AVAILABLE).count(), 1)
