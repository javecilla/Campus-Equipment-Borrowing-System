"""Exercise critical PostgreSQL constraints using stored related records."""

from datetime import timedelta

from django.db import IntegrityError, connection, transaction
from django.db.models.deletion import ProtectedError
from django.test import TestCase
from django.utils import timezone

from accounts.models import User
from borrowing.models import (
    BorrowRequest,
    Loan,
    LoanUnit,
    RequestItem,
    ReturnRecord,
    UnitAllocation,
)
from inventory.models import (
    EquipmentUnit,
    MaintenanceOutcome,
    MaintenanceRecord,
    MaintenanceStatus,
    UnitCondition,
    UnitStatus,
)
from operations.models import AuditLog, SystemSetting
from operations.tests.records import IssuedRecords, create_issued_records, create_request


class SchemaTests(TestCase):
    records: IssuedRecords

    def setUp(self) -> None:
        self.assertEqual(
            connection.vendor, "postgresql", "Foundation evidence requires PostgreSQL."
        )
        self.records = create_issued_records()

    def test_custom_user_and_initial_settings(self) -> None:
        self.assertEqual(User._meta.db_table, "accounts_user")
        setting: SystemSetting = SystemSetting.objects.get(pk=1)
        self.assertEqual((setting.max_loan_days, setting.max_quantity_per_item), (7, 3))
        self.assertIsNone(setting.updated_by_id)
        audit: AuditLog = AuditLog.objects.get(action="SETTINGS_INITIALIZED")
        self.assertEqual((audit.actor_kind, audit.actor_id, audit.target_id), ("SYSTEM", None, 1))
        with self.assertRaises(IntegrityError), transaction.atomic():
            User.objects.filter(pk=self.records.catalog.borrower.pk).update(role="TECHNICIAN")
        with self.assertRaises(IntegrityError), transaction.atomic():
            SystemSetting.objects.create(
                id=2, max_loan_days=7, max_quantity_per_item=3, updated_at=timezone.now()
            )
        with self.assertRaises(IntegrityError), transaction.atomic():
            SystemSetting.objects.filter(pk=1).update(max_quantity_per_item=0)

    def test_inventory_identity_and_condition(self) -> None:
        second_unit: EquipmentUnit = EquipmentUnit.objects.create(
            catalog_item=self.records.catalog.item,
            asset_code="TEST-CAM-002",
            condition=UnitCondition.GOOD,
            acquired_on=timezone.localdate(),
            status=UnitStatus.AVAILABLE,
        )
        for changes in (
            {"asset_code": "test-cam-001"},
            {"asset_code": " TEST-CAM-003 "},
            {"asset_code": "  "},
            {"condition": "BROKEN"},
            {"status": "UNKNOWN"},
            {"condition": UnitCondition.DAMAGED},
        ):
            with (
                self.subTest(changes=changes),
                self.assertRaises(IntegrityError),
                transaction.atomic(),
            ):
                EquipmentUnit.objects.filter(pk=second_unit.pk).update(**changes)
        EquipmentUnit.objects.filter(pk=second_unit.pk).update(
            condition=UnitCondition.DAMAGED, status=UnitStatus.MAINTENANCE
        )
        self.assertEqual(
            EquipmentUnit.objects.get(pk=second_unit.pk).status, UnitStatus.MAINTENANCE
        )
        with self.assertRaises(ProtectedError):
            self.records.catalog.item.delete()
        with self.assertRaises(ProtectedError):
            self.records.catalog.borrower.delete()

    def test_request_dates_decisions_and_quantities(self) -> None:
        request: BorrowRequest = self.records.request
        for changes in (
            {"purpose": " \t"},
            {"status": "OVERDUE"},
            {"max_loan_days_applied": 0},
            {"max_quantity_applied": 0},
            {"desired_due_date": request.submitted_on},
            {"agreed_due_date": request.submitted_on + timedelta(days=8)},
            {"decided_at": None},
            {"decided_by_id": None},
            {"decision_reason": " "},
            {"cancelled_by_id": self.records.catalog.borrower.pk},
        ):
            with (
                self.subTest(changes=changes),
                self.assertRaises(IntegrityError),
                transaction.atomic(),
            ):
                BorrowRequest.objects.filter(pk=request.pk).update(**changes)
        with self.assertRaises(IntegrityError), transaction.atomic():
            RequestItem.objects.filter(pk=self.records.request_item.pk).update(quantity=0)
        with self.assertRaises(IntegrityError), transaction.atomic():
            RequestItem.objects.create(
                request=request, catalog_item=self.records.catalog.item, quantity=1
            )
        BorrowRequest.objects.filter(pk=request.pk).update(max_loan_days_applied=2147483647)
        self.assertEqual(BorrowRequest.objects.get(pk=request.pk).max_loan_days_applied, 2147483647)

    def test_active_allocation_remains_exclusive_after_release(self) -> None:
        records: IssuedRecords = self.records
        other_item: RequestItem = create_request(
            records.catalog.borrower.pk, records.catalog.item.pk, timezone.now()
        )
        with self.assertRaises(IntegrityError), transaction.atomic():
            UnitAllocation.objects.create(
                request_item=other_item,
                unit=records.catalog.unit,
                allocated_by=records.catalog.admin,
                allocated_at=timezone.now(),
            )
        self.assertEqual(
            UnitAllocation.objects.filter(unit=records.catalog.unit, ended_at__isnull=True).count(),
            1,
        )
        for changes in (
            {"released_at": records.allocation.allocated_at - timedelta(seconds=1)},
            {"ended_at": records.allocation.allocated_at - timedelta(seconds=1)},
            {"cancelled_at": timezone.now()},
        ):
            with (
                self.subTest(changes=changes),
                self.assertRaises(IntegrityError),
                transaction.atomic(),
            ):
                UnitAllocation.objects.filter(pk=records.allocation.pk).update(**changes)
        returned_at = timezone.now()
        ReturnRecord.objects.create(
            loan_unit=records.loan_unit,
            returned_at=returned_at,
            returned_condition=UnitCondition.GOOD,
            received_by=records.catalog.admin,
        )
        UnitAllocation.objects.filter(pk=records.allocation.pk).update(ended_at=returned_at)
        UnitAllocation.objects.create(
            request_item=other_item,
            unit=records.catalog.unit,
            allocated_by=records.catalog.admin,
            allocated_at=returned_at,
        )
        self.assertEqual(
            UnitAllocation.objects.filter(unit=records.catalog.unit, ended_at__isnull=True).count(),
            1,
        )

    def test_issue_and_return_cannot_be_duplicated(self) -> None:
        records: IssuedRecords = self.records
        with self.assertRaises(IntegrityError), transaction.atomic():
            Loan.objects.create(
                request=records.request,
                issued_by=records.catalog.admin,
                issued_at=timezone.now(),
                issued_on=records.loan.issued_on,
                due_date=records.loan.due_date,
            )
        with self.assertRaises(IntegrityError), transaction.atomic():
            LoanUnit.objects.create(loan=records.loan, allocation=records.allocation)
        with self.assertRaises(IntegrityError), transaction.atomic():
            Loan.objects.filter(pk=records.loan.pk).update(
                closed_at=records.loan.issued_at - timedelta(seconds=1)
            )
        with self.assertRaises(IntegrityError), transaction.atomic():
            Loan.objects.filter(pk=records.loan.pk).update(
                due_date=records.loan.issued_on - timedelta(days=1)
            )
        returned: ReturnRecord = ReturnRecord.objects.create(
            loan_unit=records.loan_unit,
            returned_at=timezone.now(),
            returned_condition=UnitCondition.GOOD,
            received_by=records.catalog.admin,
        )
        with self.assertRaises(IntegrityError), transaction.atomic():
            ReturnRecord.objects.create(
                loan_unit=records.loan_unit,
                returned_at=timezone.now(),
                returned_condition=UnitCondition.GOOD,
                received_by=records.catalog.admin,
            )
        with self.assertRaises(IntegrityError), transaction.atomic():
            ReturnRecord.objects.filter(pk=returned.pk).update(returned_condition="UNKNOWN")

    def test_maintenance_exclusivity_and_complete_closure(self) -> None:
        unit: EquipmentUnit = EquipmentUnit.objects.create(
            catalog_item=self.records.catalog.item,
            asset_code="TEST-REPAIR-001",
            condition=UnitCondition.DAMAGED,
            acquired_on=timezone.localdate(),
            status=UnitStatus.MAINTENANCE,
        )
        record: MaintenanceRecord = MaintenanceRecord.objects.create(
            unit=unit,
            problem="Damaged test housing",
            opened_at=timezone.now(),
            opened_by=self.records.catalog.admin,
            status=MaintenanceStatus.OPEN,
        )
        with self.assertRaises(IntegrityError), transaction.atomic():
            MaintenanceRecord.objects.create(
                unit=unit,
                problem="Duplicate",
                opened_at=timezone.now(),
                opened_by=self.records.catalog.admin,
                status=MaintenanceStatus.OPEN,
            )
        with self.assertRaises(IntegrityError), transaction.atomic():
            MaintenanceRecord.objects.filter(pk=record.pk).update(status=MaintenanceStatus.CLOSED)
        with self.assertRaises(IntegrityError), transaction.atomic():
            MaintenanceRecord.objects.filter(pk=record.pk).update(
                status=MaintenanceStatus.CLOSED,
                action="Repaired",
                outcome=MaintenanceOutcome.AVAILABLE,
                closed_by=self.records.catalog.admin,
                closed_at=record.opened_at - timedelta(seconds=1),
            )
        MaintenanceRecord.objects.filter(pk=record.pk).update(
            status=MaintenanceStatus.CLOSED,
            action="Replaced housing",
            outcome=MaintenanceOutcome.AVAILABLE,
            closed_by=self.records.catalog.admin,
            closed_at=timezone.now(),
        )
        self.assertEqual(
            MaintenanceRecord.objects.get(pk=record.pk).status, MaintenanceStatus.CLOSED
        )

    def test_audit_actor_domain_and_reference_constraints(self) -> None:
        audit: AuditLog = AuditLog.objects.get(action="SETTINGS_INITIALIZED")
        for changes in (
            {"actor_id": self.records.catalog.admin.pk},
            {"actor_kind": "USER"},
            {"actor_kind": "OTHER"},
            {"action": "UNKNOWN"},
            {"target_model": "auth.User"},
            {"target_id": 0},
            {"summary": " "},
        ):
            with (
                self.subTest(changes=changes),
                self.assertRaises(IntegrityError),
                transaction.atomic(),
            ):
                AuditLog.objects.filter(pk=audit.pk).update(**changes)
