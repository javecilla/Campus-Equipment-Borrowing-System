"""Catalog and physical inventory schema; workflow writes remain explicit."""

from django.conf import settings
from django.db import models
from django.db.models.functions import Lower, Trim


class UnitCondition(models.TextChoices):
    GOOD = "GOOD", "Good"
    FAIR = "FAIR", "Fair"
    DAMAGED = "DAMAGED", "Damaged"


class UnitStatus(models.TextChoices):
    AVAILABLE = "AVAILABLE", "Available"
    RESERVED = "RESERVED", "Reserved"
    ISSUED = "ISSUED", "Issued"
    MAINTENANCE = "MAINTENANCE", "Maintenance"
    RETIRED = "RETIRED", "Retired"


class MaintenanceStatus(models.TextChoices):
    OPEN = "OPEN", "Open"
    CLOSED = "CLOSED", "Closed"


class MaintenanceOutcome(models.TextChoices):
    AVAILABLE = "AVAILABLE", "Available"
    RETIRED = "RETIRED", "Retired"


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    is_archived = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints: list[models.BaseConstraint] = [
            models.UniqueConstraint(Lower("name"), name="category_name_ci_unique"),
            models.CheckConstraint(
                condition=models.Q(name__regex=r"\S"), name="category_nonblank_name"
            ),
        ]


class CatalogItem(models.Model):
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="items")
    name = models.CharField(max_length=150)
    description = models.TextField()
    photo = models.ImageField(upload_to="equipment/", blank=True)
    is_archived = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints: list[models.BaseConstraint] = [
            models.CheckConstraint(
                condition=models.Q(name__regex=r"\S"), name="item_nonblank_name"
            ),
            models.CheckConstraint(
                condition=models.Q(description__regex=r"\S"), name="item_nonblank_description"
            ),
        ]


class EquipmentUnit(models.Model):
    catalog_item = models.ForeignKey(CatalogItem, on_delete=models.PROTECT, related_name="units")
    asset_code = models.CharField(max_length=64)
    condition = models.CharField(max_length=10, choices=UnitCondition.choices)
    acquired_on = models.DateField()
    status = models.CharField(max_length=11, choices=UnitStatus.choices)
    internal_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes: list[models.Index] = [
            models.Index(fields=["catalog_item", "status"], name="unit_item_status_idx")
        ]
        constraints: list[models.BaseConstraint] = [
            models.UniqueConstraint(Lower("asset_code"), name="unit_asset_code_ci_unique"),
            models.CheckConstraint(
                condition=models.Q(asset_code__regex=r"\S"), name="unit_nonblank_asset_code"
            ),
            models.CheckConstraint(
                condition=models.Q(asset_code=Trim("asset_code")), name="unit_trimmed_asset_code"
            ),
            models.CheckConstraint(
                condition=models.Q(condition__in=UnitCondition.values), name="unit_valid_condition"
            ),
            models.CheckConstraint(
                condition=models.Q(status__in=UnitStatus.values), name="unit_valid_status"
            ),
            models.CheckConstraint(
                condition=~models.Q(condition=UnitCondition.DAMAGED)
                | models.Q(status__in=[UnitStatus.MAINTENANCE, UnitStatus.RETIRED]),
                name="unit_damaged_unavailable",
            ),
        ]


class MaintenanceRecord(models.Model):
    unit = models.ForeignKey(
        EquipmentUnit, on_delete=models.PROTECT, related_name="maintenance_records"
    )
    source_return = models.OneToOneField(
        "borrowing.ReturnRecord",
        on_delete=models.PROTECT,
        related_name="maintenance_record",
        null=True,
        blank=True,
    )
    problem = models.TextField()
    action = models.TextField(blank=True)
    opened_at = models.DateTimeField()
    opened_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="maintenance_opened"
    )
    closed_at = models.DateTimeField(null=True, blank=True)
    closed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="maintenance_closed",
        null=True,
        blank=True,
    )
    status = models.CharField(max_length=6, choices=MaintenanceStatus.choices)
    outcome = models.CharField(
        max_length=9, choices=MaintenanceOutcome.choices, null=True, blank=True
    )

    class Meta:
        indexes: list[models.Index] = [
            models.Index(fields=["status", "opened_at"], name="maintenance_status_opened_idx")
        ]
        constraints: list[models.BaseConstraint] = [
            models.UniqueConstraint(
                fields=["unit"],
                condition=models.Q(status=MaintenanceStatus.OPEN),
                name="maintenance_one_open_unit",
            ),
            models.CheckConstraint(
                condition=models.Q(problem__regex=r"\S"), name="maintenance_nonblank_problem"
            ),
            models.CheckConstraint(
                condition=models.Q(status__in=MaintenanceStatus.values),
                name="maintenance_valid_status",
            ),
            models.CheckConstraint(
                condition=models.Q(outcome__isnull=True)
                | models.Q(outcome__in=MaintenanceOutcome.values),
                name="maintenance_valid_outcome",
            ),
            models.CheckConstraint(
                condition=models.Q(
                    status=MaintenanceStatus.OPEN,
                    closed_at__isnull=True,
                    closed_by__isnull=True,
                    outcome__isnull=True,
                )
                | models.Q(
                    status=MaintenanceStatus.CLOSED,
                    closed_at__isnull=False,
                    closed_by__isnull=False,
                    outcome__isnull=False,
                    action__regex=r"\S",
                ),
                name="maintenance_closure_complete",
            ),
            models.CheckConstraint(
                condition=models.Q(closed_at__isnull=True)
                | models.Q(closed_at__gte=models.F("opened_at")),
                name="maintenance_closure_after_open",
            ),
        ]
