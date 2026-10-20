"""T15 release/cancellation contention using real overlapping PostgreSQL transactions."""

from concurrent.futures import Future, ThreadPoolExecutor
from queue import Queue
from typing import Literal

from django.db import connection, connections, transaction
from django.test import TransactionTestCase
from django.utils import timezone

from accounts.models import User
from borrowing.models import BorrowRequest, Loan, RequestStatus, UnitAllocation
from borrowing.release_services import release_request
from borrowing.services import (
    RequestCancellationConflict,
    WorkflowConflict,
    approve_request,
    cancel_request,
)
from borrowing.tests.test_approval_concurrency import wait_for_blocked_approvals
from inventory.models import UnitStatus
from operations.models import AuditAction, AuditLog
from operations.tests.records import CatalogRecords, create_catalog_records, create_request

RaceOutcome = Literal["released", "cancelled", "conflict"]


def prepare_connection(backend_pids: Queue[int]) -> None:
    with connections["default"].cursor() as cursor:
        cursor.execute("SET lock_timeout = '10s'")
        cursor.execute("SET statement_timeout = '15s'")
        cursor.execute("SELECT pg_backend_pid()")
        backend_pids.put(cursor.fetchone()[0])


def competing_release(actor_id: int, request_id: int, backend_pids: Queue[int]) -> RaceOutcome:
    try:
        prepare_connection(backend_pids)
        try:
            release_request(actor_id, request_id)
        except WorkflowConflict:
            return "conflict"
        return "released"
    finally:
        connections["default"].close()


def competing_cancel(owner_id: int, request_id: int, backend_pids: Queue[int]) -> RaceOutcome:
    try:
        prepare_connection(backend_pids)
        try:
            cancel_request(owner_id, request_id)
        except RequestCancellationConflict:
            return "conflict"
        return "cancelled"
    finally:
        connections["default"].close()


class ReleaseConcurrencyTests(TransactionTestCase):
    records: CatalogRecords
    borrow_request: BorrowRequest

    def setUp(self) -> None:
        self.assertEqual(connection.vendor, "postgresql")
        self.records = create_catalog_records()
        request_item = create_request(
            self.records.borrower.pk, self.records.item.pk, timezone.now()
        )
        self.borrow_request = approve_request(
            self.records.admin.pk, request_item.request_id, "T15 race"
        )

    def test_duplicate_release_has_one_loan_and_one_conflict(self) -> None:
        backend_pids: Queue[int] = Queue()
        with ThreadPoolExecutor(max_workers=2) as executor:
            with transaction.atomic():
                User.objects.select_for_update().get(pk=self.records.borrower.pk)
                with connection.cursor() as cursor:
                    cursor.execute("SELECT pg_backend_pid()")
                    blocker_pid: int = cursor.fetchone()[0]
                first: Future[RaceOutcome] = executor.submit(
                    competing_release, self.records.admin.pk, self.borrow_request.pk, backend_pids
                )
                second: Future[RaceOutcome] = executor.submit(
                    competing_release, self.records.admin.pk, self.borrow_request.pk, backend_pids
                )
                worker_pids: tuple[int, int] = (
                    backend_pids.get(timeout=5),
                    backend_pids.get(timeout=5),
                )
                self.assertEqual(len({blocker_pid, *worker_pids}), 3)
                wait_for_blocked_approvals(blocker_pid, worker_pids)
            self.assertCountEqual(
                [first.result(timeout=20), second.result(timeout=20)], ["released", "conflict"]
            )
        loan = Loan.objects.get(request=self.borrow_request)
        self.assertEqual(loan.units.count(), 1)
        self.assertEqual(AuditLog.objects.filter(action=AuditAction.LOAN_RELEASED).count(), 1)
        self.borrow_request.refresh_from_db()
        self.records.unit.refresh_from_db()
        allocation = UnitAllocation.objects.get(unit=self.records.unit)
        self.assertEqual(self.borrow_request.status, RequestStatus.ISSUED)
        self.assertEqual(self.records.unit.status, UnitStatus.ISSUED)
        self.assertEqual(allocation.released_at, loan.issued_at)
        self.assertIsNone(allocation.ended_at)

    def test_cancel_and_release_have_one_complete_winner(self) -> None:
        backend_pids: Queue[int] = Queue()
        with ThreadPoolExecutor(max_workers=2) as executor:
            with transaction.atomic():
                User.objects.select_for_update().get(pk=self.records.borrower.pk)
                with connection.cursor() as cursor:
                    cursor.execute("SELECT pg_backend_pid()")
                    blocker_pid: int = cursor.fetchone()[0]
                release: Future[RaceOutcome] = executor.submit(
                    competing_release, self.records.admin.pk, self.borrow_request.pk, backend_pids
                )
                cancel: Future[RaceOutcome] = executor.submit(
                    competing_cancel, self.records.borrower.pk, self.borrow_request.pk, backend_pids
                )
                worker_pids: tuple[int, int] = (
                    backend_pids.get(timeout=5),
                    backend_pids.get(timeout=5),
                )
                self.assertEqual(len({blocker_pid, *worker_pids}), 3)
                wait_for_blocked_approvals(blocker_pid, worker_pids)
            outcomes: tuple[RaceOutcome, RaceOutcome] = (
                release.result(timeout=20),
                cancel.result(timeout=20),
            )
        self.assertEqual(outcomes.count("conflict"), 1)
        self.borrow_request.refresh_from_db()
        self.records.unit.refresh_from_db()
        allocation = UnitAllocation.objects.get(unit=self.records.unit)
        if "released" in outcomes:
            loan = Loan.objects.get(request=self.borrow_request)
            self.assertEqual(outcomes, ("released", "conflict"))
            self.assertEqual(self.borrow_request.status, RequestStatus.ISSUED)
            self.assertEqual(self.records.unit.status, UnitStatus.ISSUED)
            self.assertEqual(allocation.released_at, loan.issued_at)
            self.assertIsNone(allocation.ended_at)
            self.assertIsNone(allocation.cancelled_at)
            self.assertEqual(loan.units.count(), 1)
            expected_action = AuditAction.LOAN_RELEASED
        else:
            self.assertEqual(outcomes, ("conflict", "cancelled"))
            self.assertEqual(self.borrow_request.status, RequestStatus.CANCELLED)
            self.assertEqual(self.records.unit.status, UnitStatus.AVAILABLE)
            self.assertIsNone(allocation.released_at)
            self.assertEqual(allocation.cancelled_at, allocation.ended_at)
            self.assertIsNotNone(allocation.ended_at)
            self.assertFalse(Loan.objects.exists())
            expected_action = AuditAction.REQUEST_CANCELLED
        self.assertEqual(
            list(
                AuditLog.objects.filter(
                    action__in=(AuditAction.LOAN_RELEASED, AuditAction.REQUEST_CANCELLED)
                ).values_list("action", flat=True)
            ),
            [expected_action],
        )
