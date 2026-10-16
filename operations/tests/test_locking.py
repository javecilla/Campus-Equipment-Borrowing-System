"""Verify shared lock behavior using separate real PostgreSQL connections."""

from concurrent.futures import ThreadPoolExecutor

import psycopg
from django.db import OperationalError, connections, transaction
from django.db.transaction import TransactionManagementError
from django.test import TransactionTestCase

from inventory.models import CatalogItem, EquipmentUnit
from operations.audit import write_audit
from operations.locking import (
    LockedCatalog,
    LockedRequest,
    lock_available_units,
    lock_borrower,
    lock_catalog,
    lock_request,
    lock_units,
)
from operations.models import AuditAction, AuditTarget
from operations.tests.records import IssuedRecords, create_issued_records


def competing_request_lock(owner_id: int, request_id: int) -> str:
    try:
        with transaction.atomic():
            with connections["default"].cursor() as cursor:
                cursor.execute("SET LOCAL lock_timeout = '250ms'")
            lock_request(owner_id, request_id)
    except OperationalError as error:
        cause: BaseException | None = error.__cause__
        if isinstance(cause, psycopg.Error) and cause.sqlstate is not None:
            return cause.sqlstate
        raise
    finally:
        connections["default"].close()
    return "lock acquired"


class LockingTests(TransactionTestCase):
    records: IssuedRecords

    def setUp(self) -> None:
        self.assertEqual(connections["default"].vendor, "postgresql")
        self.records = create_issued_records()

    def test_locks_and_audit_require_explicit_transaction(self) -> None:
        with self.assertRaises(TransactionManagementError):
            lock_borrower(self.records.catalog.borrower.pk)
        with self.assertRaises(TransactionManagementError):
            lock_request(self.records.catalog.borrower.pk, self.records.request.pk)
        with self.assertRaises(TransactionManagementError):
            lock_catalog((self.records.catalog.item.pk,))
        with self.assertRaises(TransactionManagementError):
            lock_units((self.records.catalog.unit.pk,))
        with self.assertRaises(TransactionManagementError):
            lock_available_units((self.records.catalog.item.pk,))
        with self.assertRaises(TransactionManagementError):
            write_audit(
                self.records.catalog.admin.pk,
                AuditAction.CATEGORY_UPDATED,
                AuditTarget.CATEGORY,
                self.records.catalog.category.pk,
                "Missing transaction",
            )

    def test_lock_chain_returns_authoritative_rows_and_explicit_missing_errors(self) -> None:
        with transaction.atomic():
            locked: LockedRequest = lock_request(
                self.records.catalog.borrower.pk, self.records.request.pk
            )
            catalog: LockedCatalog = lock_catalog((self.records.catalog.item.pk,))
            units: tuple[EquipmentUnit, ...] = lock_units((self.records.catalog.unit.pk,))
            self.assertEqual(locked.loan.pk, self.records.loan.pk)
            self.assertEqual(catalog.categories[0].pk, self.records.catalog.category.pk)
            self.assertEqual(units[0].pk, self.records.catalog.unit.pk)
            self.assertEqual(lock_available_units((self.records.catalog.item.pk,)), ())
        with transaction.atomic(), self.assertRaises(CatalogItem.DoesNotExist):
            lock_catalog((999999,))
        with transaction.atomic(), self.assertRaises(EquipmentUnit.DoesNotExist):
            lock_units((999999,))

    def test_request_lock_blocks_a_separate_connection_until_commit(self) -> None:
        with ThreadPoolExecutor(max_workers=1) as executor:
            with transaction.atomic():
                lock_request(self.records.catalog.borrower.pk, self.records.request.pk)
                blocked = executor.submit(
                    competing_request_lock,
                    self.records.catalog.borrower.pk,
                    self.records.request.pk,
                )
                self.assertEqual(blocked.result(timeout=5), "55P03")
            released = executor.submit(
                competing_request_lock, self.records.catalog.borrower.pk, self.records.request.pk
            )
            self.assertEqual(released.result(timeout=5), "lock acquired")
