"""PostgreSQL historical workflow import, report and preservation checks."""

from datetime import date, timedelta
from io import StringIO

from django.apps import apps
from django.core import serializers
from django.core.exceptions import ValidationError
from django.core.management import call_command
from django.core.management.base import CommandError
from django.db import IntegrityError, connection
from django.db.models import Model
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from accounts.models import User
from borrowing.models import (
    BorrowRequest,
    Loan,
    LoanUnit,
    RequestItem,
    RequestStatus,
    ReturnRecord,
    UnitAllocation,
)
from inventory.models import (
    CatalogItem,
    Category,
    EquipmentUnit,
    MaintenanceRecord,
    UnitCondition,
    UnitStatus,
)
from inventory.services import open_maintenance
from operations.demo_seed import seed_demo_data
from operations.demo_transaction_plan import (
    APPROVED,
    APPROVED_CANCELLATIONS,
    CANCELLED,
    LAPTOP,
    LOANS,
    PENDING,
    REJECTED,
    SPEAKER,
)
from operations.demo_transactions import HISTORY_AS_OF, HISTORY_START, seed_demo_transactions
from operations.models import AuditAction, AuditLog
from operations.queries import (
    dashboard_snapshot,
    loan_report_rows,
    overdue_report_rows,
    report_totals,
)


class DemoTransactionTests(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        seed_demo_data("Orchard-Compass-Telescope-2026!")
        category: Category = Category.objects.create(name="Classroom equipment")
        plans = (
            *tuple(row.request for row in LOANS),
            *tuple(row[0] for row in REJECTED),
            *CANCELLED,
            *APPROVED_CANCELLATIONS,
            *APPROVED,
            *PENDING,
        )
        for index, name in enumerate(sorted({name for plan in plans for name in plan.items})):
            item: CatalogItem = CatalogItem.objects.create(
                category=category, name=name, description=f"Existing catalog record for {name}."
            )
            for number in range(2 if name == LAPTOP else 1):
                EquipmentUnit.objects.create(
                    catalog_item=item,
                    asset_code=f"EXISTING-{index:02}-{number}",
                    condition=UnitCondition.GOOD,
                    acquired_on=date(2026, 7, 1),
                    status=UnitStatus.AVAILABLE,
                )

    def test_command_imports_october_focused_history_and_real_report_totals(self) -> None:
        original_catalog: str = serializers.serialize("json", CatalogItem.objects.order_by("pk"))
        original_accounts: str = serializers.serialize("json", User.objects.order_by("pk"))
        old_audit_ids: tuple[int, ...] = tuple(
            AuditLog.objects.order_by("pk").values_list("pk", flat=True)
        )
        original_audits: str = serializers.serialize(
            "json", AuditLog.objects.filter(pk__in=old_audit_ids).order_by("pk")
        )
        output = StringIO()
        call_command("seed_demo_transactions", stdout=output)
        self.assertEqual(BorrowRequest.objects.count(), 30)
        self.assertEqual(Loan.objects.count(), 20)
        self.assertEqual(LoanUnit.objects.count(), 34)
        self.assertEqual(ReturnRecord.objects.count(), 28)
        self.assertEqual(
            set(BorrowRequest.objects.values_list("status", flat=True)), set(RequestStatus.values)
        )
        snapshot = dashboard_snapshot(HISTORY_AS_OF)
        self.assertEqual(
            tuple((point.label, point.value) for point in snapshot.monthly_issued_loans),
            (("Aug 2026", 3), ("Sep 2026", 4), ("Oct 2026", 13)),
        )
        self.assertEqual(
            (
                snapshot.cards.pending_requests,
                snapshot.cards.active_loans,
                snapshot.cards.overdue_loans,
            ),
            (3, 4, 2),
        )
        totals = report_totals(loan_report_rows(None, None, HISTORY_AS_OF))
        self.assertEqual(
            (
                totals.loan_count,
                totals.issued_quantity,
                totals.returned_quantity,
                totals.outstanding_quantity,
            ),
            (20, 34, 28, 6),
        )
        overdue = report_totals(overdue_report_rows(None, None, HISTORY_AS_OF))
        self.assertEqual((overdue.loan_count, overdue.outstanding_quantity), (2, 2))
        self.assertEqual(MaintenanceRecord.objects.count(), 1)
        repair: MaintenanceRecord = MaintenanceRecord.objects.select_related("source_return").get()
        self.assertEqual(repair.opened_at, repair.source_return.returned_at)
        self.assertEqual(repair.unit.status, UnitStatus.AVAILABLE)
        self.assertLess(repair.opened_at, repair.closed_at)
        self.assertEqual(
            serializers.serialize("json", CatalogItem.objects.order_by("pk")), original_catalog
        )
        self.assertEqual(
            serializers.serialize("json", User.objects.order_by("pk")), original_accounts
        )
        self.assertEqual(
            serializers.serialize(
                "json", AuditLog.objects.filter(pk__in=old_audit_ids).order_by("pk")
            ),
            original_audits,
        )
        for model in (
            BorrowRequest,
            RequestItem,
            UnitAllocation,
            Loan,
            LoanUnit,
            ReturnRecord,
            MaintenanceRecord,
            AuditLog,
        ):
            for record in model.objects.all():
                record.full_clean()
        for loan in Loan.objects.select_related("request"):
            self.assertGreaterEqual(loan.issued_on, HISTORY_START)
            self.assertLessEqual(loan.issued_on, HISTORY_AS_OF)
            self.assertEqual(loan.issued_on, timezone.localdate(loan.issued_at))
            self.assertEqual(loan.due_date, loan.request.agreed_due_date)
            event: AuditLog = AuditLog.objects.get(
                action=AuditAction.LOAN_RELEASED, target_id=loan.pk
            )
            self.assertEqual(event.occurred_at, loan.issued_at)
            self.assertIn(str(loan.due_date), event.summary)
        for event in AuditLog.objects.exclude(pk__in=old_audit_ids):
            self.assertGreaterEqual(timezone.localdate(event.occurred_at), HISTORY_START)
            self.assertLessEqual(timezone.localdate(event.occurred_at), HISTORY_AS_OF)
        for returned in ReturnRecord.objects.all():
            self.assertLessEqual(timezone.localdate(returned.returned_at), HISTORY_AS_OF)
        for request in BorrowRequest.objects.all():
            self.assertLessEqual(
                (request.agreed_due_date - request.submitted_on).days, request.max_loan_days_applied
            )
        admin = User.objects.get(username="andrea.mendoza")
        client = Client()
        client.force_login(admin)
        for route in (
            "operations:dashboard",
            "operations:loan-report",
            "operations:overdue-report",
            "operations:loan-export",
            "operations:overdue-export",
        ):
            self.assertEqual(client.get(reverse(route)).status_code, 200)
        borrower = User.objects.get(username="miguel.santos")
        client.force_login(borrower)
        partial: Loan = Loan.objects.get(
            request__owner=borrower, request__status=RequestStatus.PARTIALLY_RETURNED
        )
        self.assertEqual(client.get(f"/portal/loans/{partial.pk}/").status_code, 200)
        foreign: Loan = Loan.objects.exclude(request__owner=borrower).earliest("pk")
        self.assertEqual(client.get(f"/portal/loans/{foreign.pk}/").status_code, 404)
        self.assertEqual(client.get(reverse("operations:loan-report")).status_code, 403)

    def test_repeat_import_fails_without_changing_existing_history(self) -> None:
        seed_demo_transactions(timezone.localdate())
        models: tuple[type[Model], ...] = tuple(
            model
            for model in apps.get_models()
            if model._meta.app_label in ("accounts", "inventory", "borrowing", "operations")
        )
        baseline: tuple[tuple[type[Model], str], ...] = tuple(
            (model, serializers.serialize("json", model.objects.order_by("pk"))) for model in models
        )
        with self.assertRaisesMessage(ValidationError, "history already exists"):
            seed_demo_transactions(timezone.localdate())
        for model, original in baseline:
            self.assertEqual(serializers.serialize("json", model.objects.order_by("pk")), original)

    def test_missing_or_ambiguous_existing_equipment_fails_without_partial_history(self) -> None:
        speaker: CatalogItem = CatalogItem.objects.get(name=SPEAKER)
        CatalogItem.objects.filter(pk=speaker.pk).update(name="Renamed speaker")
        with self.assertRaisesMessage(ValidationError, f'existing equipment "{SPEAKER}"'):
            seed_demo_transactions(timezone.localdate())
        self.assertEqual(BorrowRequest.objects.count(), 0)
        CatalogItem.objects.filter(pk=speaker.pk).update(name=SPEAKER)
        CatalogItem.objects.create(
            category=speaker.category, name=SPEAKER, description="A duplicate catalog identity."
        )
        with self.assertRaisesMessage(ValidationError, "ambiguous"):
            seed_demo_transactions(timezone.localdate())
        self.assertEqual(BorrowRequest.objects.count(), 0)

    def test_database_audit_failure_rolls_back_the_entire_import(self) -> None:
        original_units: str = serializers.serialize("json", EquipmentUnit.objects.order_by("pk"))
        original_audits: int = AuditLog.objects.count()
        with connection.cursor() as cursor:
            cursor.execute("SET CONSTRAINTS ALL IMMEDIATE")
            cursor.execute(
                "ALTER TABLE operations_auditlog ADD CONSTRAINT test_demo_history_audit CHECK (action <> 'LOAN_RELEASED')"
            )
        with self.assertRaises(IntegrityError):
            seed_demo_transactions(timezone.localdate())
        self.assertEqual(BorrowRequest.objects.count(), 0)
        self.assertEqual(UnitAllocation.objects.count(), 0)
        self.assertEqual(Loan.objects.count(), 0)
        self.assertEqual(AuditLog.objects.count(), original_audits)
        self.assertEqual(
            serializers.serialize("json", EquipmentUnit.objects.order_by("pk")), original_units
        )

    def test_acquisition_date_conflict_rolls_back_and_invalid_reference_date_is_rejected(
        self,
    ) -> None:
        EquipmentUnit.objects.filter(catalog_item__name=SPEAKER).update(acquired_on=HISTORY_AS_OF)
        with self.assertRaisesMessage(ValidationError, "before acquisition"):
            seed_demo_transactions(timezone.localdate())
        self.assertEqual(BorrowRequest.objects.count(), 0)
        self.assertEqual(Loan.objects.count(), 0)
        with self.assertRaisesMessage(ValidationError, "actual campus date"):
            seed_demo_transactions(timezone.localdate() - timedelta(days=1))

    def test_cleanup_preserves_catalog_accounts_and_maintenance_then_stock_can_be_reseeded(
        self,
    ) -> None:
        seed_demo_transactions(timezone.localdate())
        baseline: dict[type[Model], str] = {
            model: serializers.serialize("json", model.objects.order_by("pk"))
            for model in (User, Category, CatalogItem)
        }
        maintenance: MaintenanceRecord = MaintenanceRecord.objects.get()
        maintenance_fields: dict[str, object] = MaintenanceRecord.objects.values().get(
            pk=maintenance.pk
        )
        with self.assertRaisesMessage(CommandError, "clear_borrowing_data"):
            call_command("clear_equipment_units", stdout=StringIO())
        self.assertEqual(Loan.objects.count(), 20)
        call_command("clear_borrowing_data", stdout=StringIO())
        for model in (BorrowRequest, RequestItem, UnitAllocation, Loan, LoanUnit, ReturnRecord):
            self.assertEqual(model.objects.count(), 0)
        self.assertEqual(MaintenanceRecord.objects.count(), 1)
        self.assertEqual(
            MaintenanceRecord.objects.values().get(pk=maintenance.pk),
            {**maintenance_fields, "source_return_id": None},
        )
        self.assertFalse(EquipmentUnit.objects.exclude(status=UnitStatus.AVAILABLE).exists())
        self.assertFalse(AuditLog.objects.filter(target_model__startswith="borrowing.").exists())
        call_command("clear_equipment_units", stdout=StringIO())
        self.assertEqual(EquipmentUnit.objects.count(), 0)
        self.assertEqual(MaintenanceRecord.objects.count(), 0)
        for model, original in baseline.items():
            self.assertEqual(serializers.serialize("json", model.objects.order_by("pk")), original)
        call_command(
            "seed_demo_units",
            admin_username="andrea.mendoza",
            quantity_per_item=2,
            acquired_on="2026-07-01",
            stdout=StringIO(),
        )
        seed_demo_transactions(timezone.localdate())
        self.assertEqual(Loan.objects.count(), 20)
        self.assertEqual(ReturnRecord.objects.count(), 28)

    def test_transaction_cleanup_preserves_unavailable_stock_and_rolls_back_database_failure(
        self,
    ) -> None:
        seed_demo_transactions(timezone.localdate())
        original: dict[type[Model], str] = {
            model: serializers.serialize("json", model.objects.order_by("pk"))
            for model in (BorrowRequest, ReturnRecord, MaintenanceRecord, EquipmentUnit, AuditLog)
        }
        with connection.cursor() as cursor:
            cursor.execute(
                "CREATE FUNCTION test_reject_demo_purge() RETURNS trigger LANGUAGE plpgsql AS $$ BEGIN RAISE EXCEPTION 'test purge failure' USING ERRCODE = '23514'; END; $$"
            )
            cursor.execute(
                "CREATE TRIGGER test_demo_purge BEFORE DELETE ON borrowing_borrowrequest FOR EACH ROW EXECUTE FUNCTION test_reject_demo_purge()"
            )
        with self.assertRaises(IntegrityError):
            call_command("clear_borrowing_data", stdout=StringIO())
        for model, serialized in original.items():
            self.assertEqual(
                serializers.serialize("json", model.objects.order_by("pk")), serialized
            )
        with connection.cursor() as cursor:
            cursor.execute("DROP TRIGGER test_demo_purge ON borrowing_borrowrequest")
            cursor.execute("DROP FUNCTION test_reject_demo_purge()")
        unit: EquipmentUnit = EquipmentUnit.objects.filter(status=UnitStatus.AVAILABLE).earliest(
            "pk"
        )
        admin: User = User.objects.get(username="andrea.mendoza")
        opened: MaintenanceRecord = open_maintenance(
            admin.pk, unit.pk, "Loose connector awaiting inspection."
        )
        call_command("clear_borrowing_data", stdout=StringIO())
        unit.refresh_from_db()
        self.assertEqual(unit.status, UnitStatus.MAINTENANCE)
        self.assertTrue(MaintenanceRecord.objects.filter(pk=opened.pk).exists())
