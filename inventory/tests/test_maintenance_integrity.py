"""Real PostgreSQL checks for maintenance conflicts, rollback and lock ordering."""

from concurrent.futures import Future, ThreadPoolExecutor
from queue import Queue
from threading import Barrier, Event
from time import monotonic

from django.db import IntegrityError, connection, connections, transaction
from django.test import Client, TestCase, TransactionTestCase
from django.urls import reverse
from django.utils import timezone

from accounts.models import User, UserRole
from borrowing.models import ReturnRecord
from inventory.models import (
    EquipmentUnit,
    MaintenanceOutcome,
    MaintenanceRecord,
    MaintenanceStatus,
    UnitCondition,
    UnitStatus,
)
from inventory.services import MaintenanceConflict, close_maintenance, open_maintenance
from operations.models import AuditAction, AuditLog
from operations.tests.records import (
    CatalogRecords,
    IssuedRecords,
    create_catalog_records,
    create_issued_records,
)


class MaintenanceIntegrityTests(TestCase):
    records: IssuedRecords

    @classmethod
    def setUpTestData(cls) -> None:
        cls.records = create_issued_records()

    def test_return_identifier_cannot_bypass_manual_opening(self) -> None:
        returned: ReturnRecord = ReturnRecord.objects.create(
            loan_unit=self.records.loan_unit,
            returned_at=timezone.now(),
            returned_condition=UnitCondition.GOOD,
            received_by=self.records.catalog.admin,
            notes="Fictional return used to reject the removed legacy argument.",
        )
        before: int = AuditLog.objects.count()
        # Reject the removed API before an unrelated return can bypass an Issued unit.
        with self.assertRaisesRegex(TypeError, "source_return_id"):
            open_maintenance(
                actor_id=self.records.catalog.admin.pk,
                unit_id=self.records.catalog.unit.pk,
                problem="Must not bypass eligibility",
                source_return_id=returned.pk,
            )
        self.records.catalog.unit.refresh_from_db()
        self.assertEqual(self.records.catalog.unit.status, UnitStatus.ISSUED)
        self.assertFalse(MaintenanceRecord.objects.exists())
        self.assertEqual(AuditLog.objects.count(), before)

    def test_open_audit_failure_rolls_back_unit_and_record(self) -> None:
        EquipmentUnit.objects.filter(pk=self.records.catalog.unit.pk).update(
            status=UnitStatus.AVAILABLE
        )
        before: int = AuditLog.objects.count()
        with connection.cursor() as cursor:
            cursor.execute("SET CONSTRAINTS ALL IMMEDIATE")
            cursor.execute(
                "ALTER TABLE operations_auditlog ADD CONSTRAINT test_reject_open_maintenance "
                "CHECK (action <> 'MAINTENANCE_OPENED')"
            )
        with self.assertRaises(IntegrityError):
            open_maintenance(
                self.records.catalog.admin.pk, self.records.catalog.unit.pk, "Audit rollback"
            )
        self.records.catalog.unit.refresh_from_db()
        self.assertEqual(self.records.catalog.unit.status, UnitStatus.AVAILABLE)
        self.assertFalse(MaintenanceRecord.objects.exists())
        self.assertEqual(AuditLog.objects.count(), before)

    def test_close_audit_failure_rolls_back_repair_and_closure(self) -> None:
        EquipmentUnit.objects.filter(pk=self.records.catalog.unit.pk).update(
            status=UnitStatus.AVAILABLE
        )
        record: MaintenanceRecord = open_maintenance(
            self.records.catalog.admin.pk, self.records.catalog.unit.pk, "Audit rollback"
        )
        EquipmentUnit.objects.filter(pk=self.records.catalog.unit.pk).update(
            condition=UnitCondition.DAMAGED
        )
        before: int = AuditLog.objects.count()
        with connection.cursor() as cursor:
            cursor.execute("SET CONSTRAINTS ALL IMMEDIATE")
            cursor.execute(
                "ALTER TABLE operations_auditlog ADD CONSTRAINT test_reject_close_maintenance "
                "CHECK (action <> 'MAINTENANCE_CLOSED')"
            )
        with self.assertRaises(IntegrityError):
            close_maintenance(
                self.records.catalog.admin.pk,
                record.pk,
                "Repaired",
                MaintenanceOutcome.AVAILABLE,
                UnitCondition.GOOD,
            )
        record.refresh_from_db()
        self.records.catalog.unit.refresh_from_db()
        self.assertEqual(record.status, MaintenanceStatus.OPEN)
        self.assertIsNone(record.closed_at)
        self.assertIsNone(record.closed_by_id)
        self.assertIsNone(record.outcome)
        self.assertEqual(self.records.catalog.unit.status, UnitStatus.MAINTENANCE)
        self.assertEqual(self.records.catalog.unit.condition, UnitCondition.DAMAGED)
        self.assertEqual(AuditLog.objects.count(), before)

    def test_changed_unit_state_returns_http_conflict_without_closure(self) -> None:
        EquipmentUnit.objects.filter(pk=self.records.catalog.unit.pk).update(
            status=UnitStatus.AVAILABLE
        )
        record: MaintenanceRecord = open_maintenance(
            self.records.catalog.admin.pk, self.records.catalog.unit.pk, "Changed state"
        )
        EquipmentUnit.objects.filter(pk=self.records.catalog.unit.pk).update(
            status=UnitStatus.RETIRED
        )
        self.client.force_login(self.records.catalog.admin)
        before: int = AuditLog.objects.count()
        response = self.client.post(
            reverse("inventory_manage:maintenance-close", args=[record.pk]),
            {"action": "Repair", "outcome": MaintenanceOutcome.AVAILABLE},
        )
        self.assertContains(response, "not currently in maintenance", status_code=409)
        record.refresh_from_db()
        self.records.catalog.unit.refresh_from_db()
        self.assertEqual(record.status, MaintenanceStatus.OPEN)
        self.assertEqual(self.records.catalog.unit.status, UnitStatus.RETIRED)
        self.assertEqual(AuditLog.objects.count(), before)

    def test_csrf_and_protected_fields_across_manual_open_and_close(self) -> None:
        EquipmentUnit.objects.filter(pk=self.records.catalog.unit.pk).update(
            status=UnitStatus.AVAILABLE
        )
        client: Client = Client(enforce_csrf_checks=True)
        client.force_login(self.records.catalog.admin)
        create_url: str = reverse("inventory_manage:maintenance-create")
        self.assertEqual(client.post(create_url, {}).status_code, 403)
        self.assertFalse(MaintenanceRecord.objects.exists())
        self.assertEqual(client.get(create_url).status_code, 200)
        token: str = client.cookies["csrftoken"].value
        response = client.post(
            create_url,
            {
                "csrfmiddlewaretoken": token,
                "unit": self.records.catalog.unit.pk,
                "problem": "Manual input allowlist",
                "source_return_id": self.records.loan_unit.pk,
                "opened_by": self.records.catalog.borrower.pk,
                "status": MaintenanceStatus.CLOSED,
            },
        )
        self.assertEqual(response.status_code, 302)
        record: MaintenanceRecord = MaintenanceRecord.objects.get()
        self.assertIsNone(record.source_return_id)
        self.assertEqual(record.opened_by_id, self.records.catalog.admin.pk)
        self.assertEqual(record.status, MaintenanceStatus.OPEN)
        close_url: str = reverse("inventory_manage:maintenance-close", args=[record.pk])
        self.assertEqual(client.post(close_url, {}).status_code, 403)
        record.refresh_from_db()
        self.assertEqual(record.status, MaintenanceStatus.OPEN)
        response = client.post(
            close_url,
            {
                "csrfmiddlewaretoken": token,
                "action": "Repaired",
                "outcome": MaintenanceOutcome.AVAILABLE,
                "closed_by": self.records.catalog.borrower.pk,
                "status": MaintenanceStatus.OPEN,
            },
        )
        self.assertEqual(response.status_code, 302)
        record.refresh_from_db()
        self.assertEqual(record.closed_by_id, self.records.catalog.admin.pk)
        self.assertEqual(record.status, MaintenanceStatus.CLOSED)


def competing_manual_open(actor_id: int, unit_id: int, barrier: Barrier) -> str:
    try:
        barrier.wait(timeout=5)
        open_maintenance(actor_id, unit_id, "Competing manual opening")
    except MaintenanceConflict:
        return "conflict"
    finally:
        connections["default"].close()
    return "opened"


def competing_close(actor_id: int, maintenance_id: int, backend_ids: Queue[int]) -> int:
    try:
        with connections["default"].cursor() as cursor:
            cursor.execute("SET statement_timeout = '5s'")
            cursor.execute("SELECT pg_backend_pid()")
            backend_ids.put(cursor.fetchone()[0])
        return close_maintenance(
            actor_id, maintenance_id, "Repaired", MaintenanceOutcome.AVAILABLE, UnitCondition.GOOD
        ).pk
    finally:
        connections["default"].close()


class MaintenanceConcurrencyTests(TransactionTestCase):
    records: CatalogRecords

    def setUp(self) -> None:
        self.assertEqual(connection.vendor, "postgresql")
        self.records = create_catalog_records()

    def test_competing_admins_open_exactly_one_record_and_audit(self) -> None:
        other_admin: User = User.objects.create_user(
            username="other_maintenance_admin", password=None, role=UserRole.ADMIN
        )
        barrier: Barrier = Barrier(2)
        with ThreadPoolExecutor(max_workers=2) as executor:
            first: Future[str] = executor.submit(
                competing_manual_open, self.records.admin.pk, self.records.unit.pk, barrier
            )
            second: Future[str] = executor.submit(
                competing_manual_open, other_admin.pk, self.records.unit.pk, barrier
            )
            self.assertCountEqual(
                [first.result(timeout=10), second.result(timeout=10)], ["opened", "conflict"]
            )
        self.records.unit.refresh_from_db()
        self.assertEqual(self.records.unit.status, UnitStatus.MAINTENANCE)
        self.assertEqual(MaintenanceRecord.objects.filter(status=MaintenanceStatus.OPEN).count(), 1)
        self.assertEqual(AuditLog.objects.filter(action=AuditAction.MAINTENANCE_OPENED).count(), 1)

    def test_closure_waits_for_unit_without_locking_maintenance_first(self) -> None:
        record: MaintenanceRecord = open_maintenance(
            self.records.admin.pk, self.records.unit.pk, "Lock ordering"
        )
        backend_ids: Queue[int] = Queue()
        pause: Event = Event()
        with ThreadPoolExecutor(max_workers=1) as executor:
            with transaction.atomic():
                EquipmentUnit.objects.select_for_update().get(pk=self.records.unit.pk)
                closed: Future[int] = executor.submit(
                    competing_close, self.records.admin.pk, record.pk, backend_ids
                )
                backend_id: int = backend_ids.get(timeout=5)
                deadline: float = monotonic() + 3
                while True:
                    with connection.cursor() as cursor:
                        cursor.execute(
                            "SELECT wait_event_type FROM pg_stat_activity WHERE pid = %s",
                            [backend_id],
                        )
                        waiting: tuple[str | None] = cursor.fetchone()
                    if waiting[0] == "Lock":
                        break
                    if monotonic() >= deadline:
                        self.fail("Competing closure did not wait for the locked unit within 3s.")
                    pause.wait(0.01)
                MaintenanceRecord.objects.select_for_update(nowait=True).get(pk=record.pk)
            self.assertEqual(closed.result(timeout=10), record.pk)
        record.refresh_from_db()
        self.records.unit.refresh_from_db()
        self.assertEqual(record.status, MaintenanceStatus.CLOSED)
        self.assertEqual(self.records.unit.status, UnitStatus.AVAILABLE)
