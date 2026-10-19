"""T16 equipment maintenance and inventory reconciliation integration checks."""

from datetime import date

from django.core.exceptions import PermissionDenied, ValidationError
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from accounts.models import Profile, User, UserRole
from inventory.models import (
    CatalogItem,
    Category,
    EquipmentUnit,
    MaintenanceOutcome,
    MaintenanceRecord,
    MaintenanceStatus,
    UnitCondition,
    UnitStatus,
)
from inventory.queries import get_overall_inventory_counts
from inventory.services import close_maintenance, open_maintenance
from operations.models import AuditAction, AuditLog, AuditTarget


def create_test_user(username: str, role: UserRole, is_active: bool) -> User:
    """Create a test user with an associated Profile without default arguments."""
    user: User = User.objects.create_user(
        username=username,
        email=f"{username}@example.invalid",
        password="TestPassword123!",
        first_name="Fictional",
        last_name="Maintainer",
        role=role,
        is_active=is_active,
    )
    Profile.objects.create(user=user, contact_number="09123456789")
    return user


class MaintenanceServiceTests(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.admin: User = create_test_user("maint_admin", UserRole.ADMIN, True)
        cls.borrower: User = create_test_user("maint_borrower", UserRole.BASIC_USER, True)
        cls.inactive_admin: User = create_test_user("maint_inactive", UserRole.ADMIN, False)

        cls.category: Category = Category.objects.create(
            name="Lab Equipment",
            description="Laboratory and measuring gear.",
            is_archived=False,
        )
        cls.item: CatalogItem = CatalogItem.objects.create(
            category=cls.category,
            name="Digital Oscilloscope",
            description="100MHz Dual Channel Oscilloscope",
            is_archived=False,
        )
        cls.available_unit: EquipmentUnit = EquipmentUnit.objects.create(
            catalog_item=cls.item,
            asset_code="OSC-001",
            condition=UnitCondition.GOOD,
            acquired_on=date(2025, 1, 15),
            status=UnitStatus.AVAILABLE,
            internal_notes="Unit in primary lab.",
        )
        cls.reserved_unit: EquipmentUnit = EquipmentUnit.objects.create(
            catalog_item=cls.item,
            asset_code="OSC-002",
            condition=UnitCondition.GOOD,
            acquired_on=date(2025, 1, 15),
            status=UnitStatus.RESERVED,
            internal_notes="Allocated for upcoming session.",
        )
        cls.issued_unit: EquipmentUnit = EquipmentUnit.objects.create(
            catalog_item=cls.item,
            asset_code="OSC-003",
            condition=UnitCondition.GOOD,
            acquired_on=date(2025, 1, 15),
            status=UnitStatus.ISSUED,
            internal_notes="Currently checked out.",
        )
        cls.retired_unit: EquipmentUnit = EquipmentUnit.objects.create(
            catalog_item=cls.item,
            asset_code="OSC-004",
            condition=UnitCondition.DAMAGED,
            acquired_on=date(2024, 1, 15),
            status=UnitStatus.RETIRED,
            internal_notes="Decommissioned unit.",
        )

    def test_open_maintenance_on_available_unit_success(self) -> None:
        unit: EquipmentUnit = self.available_unit
        problem_text: str = "Screen flickers intermittently under load."

        record: MaintenanceRecord = open_maintenance(
            actor_id=self.admin.pk,
            unit_id=unit.pk,
            problem=problem_text,
            source_return_id=None,
        )

        unit.refresh_from_db()
        self.assertEqual(unit.status, UnitStatus.MAINTENANCE)
        self.assertEqual(record.status, MaintenanceStatus.OPEN)
        self.assertEqual(record.problem, problem_text)
        self.assertEqual(record.action, "")
        self.assertIsNone(record.outcome)
        self.assertIsNone(record.closed_at)
        self.assertIsNone(record.closed_by)
        self.assertEqual(record.opened_by, self.admin)

        audit: AuditLog | None = AuditLog.objects.filter(
            action=AuditAction.MAINTENANCE_OPENED,
            target_model=AuditTarget.MAINTENANCE_RECORD,
            target_id=record.pk,
        ).first()
        self.assertIsNotNone(audit)
        if audit is not None:
            self.assertEqual(audit.actor, self.admin)
            self.assertIn("OSC-001", audit.summary)
            self.assertIn("Screen flickers", audit.summary)

    def test_open_maintenance_rejects_reserved_unit(self) -> None:
        with self.assertRaises(ValidationError) as ctx:
            open_maintenance(
                actor_id=self.admin.pk,
                unit_id=self.reserved_unit.pk,
                problem="Faulty knob",
                source_return_id=None,
            )
        self.assertIn("reserved", str(ctx.exception).lower())

    def test_open_maintenance_rejects_issued_unit(self) -> None:
        with self.assertRaises(ValidationError) as ctx:
            open_maintenance(
                actor_id=self.admin.pk,
                unit_id=self.issued_unit.pk,
                problem="Faulty probe",
                source_return_id=None,
            )
        self.assertIn("issued", str(ctx.exception).lower())

    def test_open_maintenance_rejects_retired_unit(self) -> None:
        with self.assertRaises(ValidationError) as ctx:
            open_maintenance(
                actor_id=self.admin.pk,
                unit_id=self.retired_unit.pk,
                problem="Cannot repair",
                source_return_id=None,
            )
        self.assertIn("retired", str(ctx.exception).lower())

    def test_open_maintenance_rejects_already_in_maintenance(self) -> None:
        open_maintenance(
            actor_id=self.admin.pk,
            unit_id=self.available_unit.pk,
            problem="First problem",
            source_return_id=None,
        )

        with self.assertRaises(ValidationError) as ctx:
            open_maintenance(
                actor_id=self.admin.pk,
                unit_id=self.available_unit.pk,
                problem="Second problem",
                source_return_id=None,
            )
        self.assertIn("already in maintenance", str(ctx.exception).lower())

    def test_open_maintenance_rejects_blank_problem(self) -> None:
        with self.assertRaises(ValidationError) as ctx:
            open_maintenance(
                actor_id=self.admin.pk,
                unit_id=self.available_unit.pk,
                problem="   ",
                source_return_id=None,
            )
        self.assertIn("Problem description is required", str(ctx.exception))

    def test_open_maintenance_rejects_inactive_admin(self) -> None:
        with self.assertRaises(PermissionDenied):
            open_maintenance(
                actor_id=self.inactive_admin.pk,
                unit_id=self.available_unit.pk,
                problem="Valid problem",
                source_return_id=None,
            )

    def test_close_maintenance_with_available_outcome(self) -> None:
        record: MaintenanceRecord = open_maintenance(
            actor_id=self.admin.pk,
            unit_id=self.available_unit.pk,
            problem="Broken power switch",
            source_return_id=None,
        )

        closed: MaintenanceRecord = close_maintenance(
            actor_id=self.admin.pk,
            maintenance_id=record.pk,
            action="Replaced power switch and tested electrical conductivity.",
            outcome=MaintenanceOutcome.AVAILABLE,
            repaired_condition=UnitCondition.GOOD,
        )

        self.available_unit.refresh_from_db()
        self.assertEqual(self.available_unit.status, UnitStatus.AVAILABLE)
        self.assertEqual(self.available_unit.condition, UnitCondition.GOOD)
        self.assertEqual(closed.status, MaintenanceStatus.CLOSED)
        self.assertEqual(closed.outcome, MaintenanceOutcome.AVAILABLE)
        self.assertEqual(closed.closed_by, self.admin)
        self.assertIsNotNone(closed.closed_at)
        self.assertIn("Replaced power switch", closed.action)

        audit: AuditLog | None = AuditLog.objects.filter(
            action=AuditAction.MAINTENANCE_CLOSED,
            target_model=AuditTarget.MAINTENANCE_RECORD,
            target_id=closed.pk,
        ).first()
        self.assertIsNotNone(audit)
        if audit is not None:
            self.assertEqual(audit.actor, self.admin)
            self.assertIn("Available", audit.summary)

    def test_close_maintenance_with_retired_outcome(self) -> None:
        record: MaintenanceRecord = open_maintenance(
            actor_id=self.admin.pk,
            unit_id=self.available_unit.pk,
            problem="Main motherboard fried; unrepairable.",
            source_return_id=None,
        )

        closed: MaintenanceRecord = close_maintenance(
            actor_id=self.admin.pk,
            maintenance_id=record.pk,
            action="Deemed beyond economical repair. Harvested spare screws and retired.",
            outcome=MaintenanceOutcome.RETIRED,
            repaired_condition=None,
        )

        self.available_unit.refresh_from_db()
        self.assertEqual(self.available_unit.status, UnitStatus.RETIRED)
        self.assertEqual(closed.status, MaintenanceStatus.CLOSED)
        self.assertEqual(closed.outcome, MaintenanceOutcome.RETIRED)

        audit: AuditLog | None = AuditLog.objects.filter(
            action=AuditAction.MAINTENANCE_CLOSED,
            target_model=AuditTarget.MAINTENANCE_RECORD,
            target_id=closed.pk,
        ).first()
        self.assertIsNotNone(audit)
        if audit is not None:
            self.assertIn("Retired", audit.summary)

    def test_close_maintenance_rejects_already_closed(self) -> None:
        record: MaintenanceRecord = open_maintenance(
            actor_id=self.admin.pk,
            unit_id=self.available_unit.pk,
            problem="Lens smudges",
            source_return_id=None,
        )
        close_maintenance(
            actor_id=self.admin.pk,
            maintenance_id=record.pk,
            action="Cleaned lens",
            outcome=MaintenanceOutcome.AVAILABLE,
            repaired_condition=UnitCondition.GOOD,
        )

        with self.assertRaises(ValidationError) as ctx:
            close_maintenance(
                actor_id=self.admin.pk,
                maintenance_id=record.pk,
                action="Cleaned again",
                outcome=MaintenanceOutcome.AVAILABLE,
                repaired_condition=UnitCondition.GOOD,
            )
        self.assertIn("already closed", str(ctx.exception).lower())

    def test_close_maintenance_rejects_blank_action(self) -> None:
        record: MaintenanceRecord = open_maintenance(
            actor_id=self.admin.pk,
            unit_id=self.available_unit.pk,
            problem="Loose casing",
            source_return_id=None,
        )

        with self.assertRaises(ValidationError) as ctx:
            close_maintenance(
                actor_id=self.admin.pk,
                maintenance_id=record.pk,
                action="   ",
                outcome=MaintenanceOutcome.AVAILABLE,
                repaired_condition=UnitCondition.GOOD,
            )
        self.assertIn("Action taken is required", str(ctx.exception))

    def test_inventory_count_reconciliation_through_lifecycle(self) -> None:
        initial_counts = get_overall_inventory_counts()
        self.assertEqual(initial_counts.available, 1)
        self.assertEqual(initial_counts.reserved, 1)
        self.assertEqual(initial_counts.issued, 1)
        self.assertEqual(initial_counts.maintenance, 0)
        self.assertEqual(initial_counts.retired, 1)
        self.assertEqual(initial_counts.total, 4)

        record: MaintenanceRecord = open_maintenance(
            actor_id=self.admin.pk,
            unit_id=self.available_unit.pk,
            problem="Calibration needed",
            source_return_id=None,
        )
        in_maint_counts = get_overall_inventory_counts()
        self.assertEqual(in_maint_counts.available, 0)
        self.assertEqual(in_maint_counts.maintenance, 1)
        self.assertEqual(in_maint_counts.total, 4)

        close_maintenance(
            actor_id=self.admin.pk,
            maintenance_id=record.pk,
            action="Calibrated to factory spec",
            outcome=MaintenanceOutcome.AVAILABLE,
            repaired_condition=UnitCondition.GOOD,
        )
        restored_counts = get_overall_inventory_counts()
        self.assertEqual(restored_counts.available, 1)
        self.assertEqual(restored_counts.maintenance, 0)
        self.assertEqual(restored_counts.total, 4)


class MaintenanceViewTests(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.admin: User = create_test_user("view_admin", UserRole.ADMIN, True)
        cls.borrower: User = create_test_user("view_borrower", UserRole.BASIC_USER, True)
        cls.inactive_admin: User = create_test_user("view_inactive", UserRole.ADMIN, False)

        cls.category: Category = Category.objects.create(
            name="Audio Production",
            description="Microphones, preamps, and monitors.",
            is_archived=False,
        )
        cls.item: CatalogItem = CatalogItem.objects.create(
            category=cls.category,
            name="Studio Condenser Mic",
            description="Large diaphragm cardioid condenser mic.",
            is_archived=False,
        )
        cls.unit_available: EquipmentUnit = EquipmentUnit.objects.create(
            catalog_item=cls.item,
            asset_code="MIC-101",
            condition=UnitCondition.GOOD,
            acquired_on=date(2025, 2, 1),
            status=UnitStatus.AVAILABLE,
            internal_notes="Studio booth mic.",
        )
        cls.unit_in_maint: EquipmentUnit = EquipmentUnit.objects.create(
            catalog_item=cls.item,
            asset_code="MIC-102",
            condition=UnitCondition.DAMAGED,
            acquired_on=date(2025, 2, 1),
            status=UnitStatus.MAINTENANCE,
            internal_notes="Bent shockmount frame.",
        )
        cls.open_record: MaintenanceRecord = MaintenanceRecord.objects.create(
            unit=cls.unit_in_maint,
            source_return=None,
            problem="Dent in grill and bent frame.",
            action="",
            opened_at=timezone.now(),
            opened_by=cls.admin,
            status=MaintenanceStatus.OPEN,
            closed_at=None,
            closed_by=None,
            outcome=None,
        )

    def test_anonymous_redirected_to_login(self) -> None:
        routes: list[str] = [
            reverse("inventory_manage:maintenance-list"),
            reverse("inventory_manage:maintenance-create"),
            reverse("inventory_manage:maintenance-detail", args=[self.open_record.pk]),
            reverse("inventory_manage:maintenance-close", args=[self.open_record.pk]),
        ]
        for route in routes:
            with self.subTest(route=route):
                response = self.client.get(route)
                self.assertEqual(response.status_code, 302)
                self.assertIn(reverse("accounts:login"), response["Location"])

    def test_basic_user_forbidden(self) -> None:
        self.client.force_login(self.borrower)
        routes: list[str] = [
            reverse("inventory_manage:maintenance-list"),
            reverse("inventory_manage:maintenance-create"),
            reverse("inventory_manage:maintenance-detail", args=[self.open_record.pk]),
            reverse("inventory_manage:maintenance-close", args=[self.open_record.pk]),
        ]
        for route in routes:
            with self.subTest(route=route):
                response = self.client.get(route)
                self.assertEqual(response.status_code, 403)

    def test_maintenance_list_displays_records_and_inventory_counts(self) -> None:
        self.client.force_login(self.admin)
        response = self.client.get(reverse("inventory_manage:maintenance-list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Equipment maintenance")
        self.assertContains(response, "MIC-102")
        self.assertContains(response, "Dent in grill")
        self.assertContains(response, 'data-testid="count-maintenance"')
        self.assertContains(response, 'data-testid="open-maintenance-button"')

    def test_maintenance_list_search_filter(self) -> None:
        self.client.force_login(self.admin)
        url: str = reverse("inventory_manage:maintenance-list")

        res_found = self.client.get(url, {"q": "MIC-102"})
        self.assertEqual(res_found.status_code, 200)
        self.assertContains(res_found, "MIC-102")

        res_not_found = self.client.get(url, {"q": "NONEXISTENT-CODE"})
        self.assertEqual(res_not_found.status_code, 200)
        self.assertContains(res_not_found, "No maintenance records found")

    def test_maintenance_list_status_filter(self) -> None:
        self.client.force_login(self.admin)
        url: str = reverse("inventory_manage:maintenance-list")

        res_open = self.client.get(url, {"status": "OPEN"})
        self.assertEqual(res_open.status_code, 200)
        self.assertContains(res_open, "MIC-102")

        res_closed = self.client.get(url, {"status": "CLOSED"})
        self.assertEqual(res_closed.status_code, 200)
        self.assertContains(res_closed, "No maintenance records found")

    def test_maintenance_detail_displays_record(self) -> None:
        self.client.force_login(self.admin)
        response = self.client.get(
            reverse("inventory_manage:maintenance-detail", args=[self.open_record.pk])
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "MIC-102")
        self.assertContains(response, "Dent in grill and bent frame.")
        self.assertContains(response, "Close maintenance")

    def test_maintenance_detail_404_for_missing_record(self) -> None:
        self.client.force_login(self.admin)
        response = self.client.get(reverse("inventory_manage:maintenance-detail", args=[999999]))
        self.assertEqual(response.status_code, 404)

    def test_maintenance_create_get(self) -> None:
        self.client.force_login(self.admin)
        response = self.client.get(reverse("inventory_manage:maintenance-create"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Open maintenance")
        self.assertContains(response, "MIC-101")
        # Unit already in maintenance should not be selectable
        self.assertNotContains(response, 'value="' + str(self.unit_in_maint.pk) + '"')

    def test_maintenance_create_post_success(self) -> None:
        self.client.force_login(self.admin)
        response = self.client.post(
            reverse("inventory_manage:maintenance-create"),
            {
                "unit": self.unit_available.pk,
                "problem": "Headphone jack loose, cuts audio in left ear.",
            },
        )
        self.unit_available.refresh_from_db()
        self.assertEqual(self.unit_available.status, UnitStatus.MAINTENANCE)

        record: MaintenanceRecord = MaintenanceRecord.objects.get(
            unit=self.unit_available, status=MaintenanceStatus.OPEN
        )
        self.assertRedirects(
            response, reverse("inventory_manage:maintenance-detail", args=[record.pk])
        )

    def test_maintenance_create_post_validation_error(self) -> None:
        self.client.force_login(self.admin)
        response = self.client.post(
            reverse("inventory_manage:maintenance-create"),
            {
                "unit": self.unit_available.pk,
                "problem": "   ",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Problem description cannot be blank")

    def test_maintenance_close_get(self) -> None:
        self.client.force_login(self.admin)
        response = self.client.get(
            reverse("inventory_manage:maintenance-close", args=[self.open_record.pk])
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Close maintenance")
        self.assertContains(response, "MIC-102")

    def test_maintenance_close_post_success_available(self) -> None:
        self.client.force_login(self.admin)
        response = self.client.post(
            reverse("inventory_manage:maintenance-close", args=[self.open_record.pk]),
            {
                "action": "Straightened frame, replaced protective grill.",
                "outcome": MaintenanceOutcome.AVAILABLE,
                "repaired_condition": UnitCondition.GOOD,
            },
        )
        self.assertRedirects(
            response,
            reverse("inventory_manage:maintenance-detail", args=[self.open_record.pk]),
        )
        self.open_record.refresh_from_db()
        self.assertEqual(self.open_record.status, MaintenanceStatus.CLOSED)
        self.assertEqual(self.open_record.outcome, MaintenanceOutcome.AVAILABLE)
        self.unit_in_maint.refresh_from_db()
        self.assertEqual(self.unit_in_maint.status, UnitStatus.AVAILABLE)
        self.assertEqual(self.unit_in_maint.condition, UnitCondition.GOOD)

    def test_maintenance_close_post_success_retired(self) -> None:
        self.client.force_login(self.admin)
        response = self.client.post(
            reverse("inventory_manage:maintenance-close", args=[self.open_record.pk]),
            {
                "action": "Internal element cracked, parts unavailable. Decommissioning unit.",
                "outcome": MaintenanceOutcome.RETIRED,
                "repaired_condition": "",
            },
        )
        self.assertRedirects(
            response,
            reverse("inventory_manage:maintenance-detail", args=[self.open_record.pk]),
        )
        self.open_record.refresh_from_db()
        self.assertEqual(self.open_record.status, MaintenanceStatus.CLOSED)
        self.assertEqual(self.open_record.outcome, MaintenanceOutcome.RETIRED)
        self.unit_in_maint.refresh_from_db()
        self.assertEqual(self.unit_in_maint.status, UnitStatus.RETIRED)

    def test_maintenance_close_get_already_closed_redirects(self) -> None:
        self.client.force_login(self.admin)
        close_maintenance(
            actor_id=self.admin.pk,
            maintenance_id=self.open_record.pk,
            action="Quick repair",
            outcome=MaintenanceOutcome.AVAILABLE,
            repaired_condition=UnitCondition.GOOD,
        )
        response = self.client.get(
            reverse("inventory_manage:maintenance-close", args=[self.open_record.pk])
        )
        self.assertRedirects(
            response,
            reverse("inventory_manage:maintenance-detail", args=[self.open_record.pk]),
        )
