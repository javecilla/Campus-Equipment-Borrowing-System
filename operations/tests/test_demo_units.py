"""Real stock registration, preservation and rollback checks for CLI preparation."""

from datetime import date
from io import StringIO

from django.core import serializers
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase

from inventory.models import CatalogItem, Category, EquipmentUnit, UnitCondition, UnitStatus
from operations.demo_seed import seed_demo_data
from operations.models import AuditAction, AuditLog


class DemoUnitTests(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        seed_demo_data("Orchard-Compass-Telescope-2026!")
        category: Category = Category.objects.create(name="Computing")
        for name in ("Laptop", "USB-C Hub"):
            CatalogItem.objects.create(
                category=category,
                name=name,
                description=f"Loanable {name}.",
                photo=f"equipment/{name}.webp",
            )

    def test_top_up_is_audited_preserves_existing_units_and_is_repeatable(self) -> None:
        item: CatalogItem = CatalogItem.objects.get(name="Laptop")
        existing: EquipmentUnit = EquipmentUnit.objects.create(
            catalog_item=item,
            asset_code="ORIGINAL-001",
            condition=UnitCondition.FAIR,
            acquired_on=date(2026, 6, 1),
            status=UnitStatus.RETIRED,
        )
        baseline: str = serializers.serialize("json", EquipmentUnit.objects.filter(pk=existing.pk))
        catalog: str = serializers.serialize("json", CatalogItem.objects.order_by("pk"))
        Category.objects.create(name="Archived", is_archived=True)
        CatalogItem.objects.create(
            category=Category.objects.get(name="Archived"),
            name="Archived equipment",
            description="Stored equipment.",
        )
        for _ in range(2):
            call_command(
                "seed_demo_units",
                admin_username="andrea.mendoza",
                quantity_per_item=2,
                acquired_on="2026-07-01",
                stdout=StringIO(),
            )
        self.assertEqual(EquipmentUnit.objects.count(), 4)
        self.assertEqual(AuditLog.objects.filter(action=AuditAction.UNIT_CREATED).count(), 3)
        call_command("clear_borrowing_data", stdout=StringIO())
        self.assertEqual(
            serializers.serialize("json", EquipmentUnit.objects.filter(pk=existing.pk)), baseline
        )
        self.assertEqual(
            serializers.serialize(
                "json", CatalogItem.objects.exclude(name="Archived equipment").order_by("pk")
            ),
            catalog,
        )
        self.assertFalse(
            EquipmentUnit.objects.filter(catalog_item__name="Archived equipment").exists()
        )

    def test_invalid_input_and_asset_collision_never_leave_partial_stock(self) -> None:
        for options in (
            {
                "admin_username": "miguel.santos",
                "quantity_per_item": 2,
                "acquired_on": "2026-07-01",
            },
            {"admin_username": "missing", "quantity_per_item": 2, "acquired_on": "2026-07-01"},
            {
                "admin_username": "andrea.mendoza",
                "quantity_per_item": 0,
                "acquired_on": "2026-07-01",
            },
            {
                "admin_username": "andrea.mendoza",
                "quantity_per_item": 2,
                "acquired_on": "not-a-date",
            },
            {
                "admin_username": "andrea.mendoza",
                "quantity_per_item": 2,
                "acquired_on": "2099-01-01",
            },
        ):
            with self.assertRaises(CommandError):
                call_command("seed_demo_units", **options, stdout=StringIO())
        laptop: CatalogItem = CatalogItem.objects.get(name="Laptop")
        hub: CatalogItem = CatalogItem.objects.get(name="USB-C Hub")
        EquipmentUnit.objects.create(
            catalog_item=laptop,
            asset_code=f"DEMO-{hub.pk:04d}-001",
            condition=UnitCondition.GOOD,
            acquired_on=date(2026, 7, 1),
            status=UnitStatus.AVAILABLE,
        )
        original_audits: int = AuditLog.objects.count()
        with self.assertRaisesMessage(CommandError, "asset code already exists"):
            call_command(
                "seed_demo_units",
                admin_username="andrea.mendoza",
                quantity_per_item=2,
                acquired_on="2026-07-01",
                stdout=StringIO(),
            )
        self.assertEqual(EquipmentUnit.objects.count(), 1)
        self.assertEqual(AuditLog.objects.count(), original_audits)
