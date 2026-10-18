"""Typed operational settings and append-only business audit records."""

from django.conf import settings
from django.db import models


class AuditActorKind(models.TextChoices):
    USER = "USER", "User"
    SYSTEM = "SYSTEM", "System"


class AuditAction(models.TextChoices):
    SETTINGS_INITIALIZED = "SETTINGS_INITIALIZED", "Settings initialized"
    REQUEST_APPROVED = "REQUEST_APPROVED", "Request approved"
    REQUEST_REJECTED = "REQUEST_REJECTED", "Request rejected"
    REQUEST_CANCELLED = "REQUEST_CANCELLED", "Request cancelled"
    DUE_DATE_REVISED = "DUE_DATE_REVISED", "Due date revised"
    LOAN_RELEASED = "LOAN_RELEASED", "Loan released"
    UNIT_RETURNED = "UNIT_RETURNED", "Unit returned"
    MAINTENANCE_OPENED = "MAINTENANCE_OPENED", "Maintenance opened"
    MAINTENANCE_CLOSED = "MAINTENANCE_CLOSED", "Maintenance closed"
    ACCOUNT_CREATED = "ACCOUNT_CREATED", "Account created"
    ACCOUNT_UPDATED = "ACCOUNT_UPDATED", "Account updated"
    ACCOUNT_ACTIVATED = "ACCOUNT_ACTIVATED", "Account activated"
    ACCOUNT_DEACTIVATED = "ACCOUNT_DEACTIVATED", "Account deactivated"
    CATEGORY_CREATED = "CATEGORY_CREATED", "Category created"
    CATEGORY_UPDATED = "CATEGORY_UPDATED", "Category updated"
    CATEGORY_ARCHIVED = "CATEGORY_ARCHIVED", "Category archived"
    CATEGORY_RESTORED = "CATEGORY_RESTORED", "Category restored"
    ITEM_CREATED = "ITEM_CREATED", "Item created"
    ITEM_UPDATED = "ITEM_UPDATED", "Item updated"
    ITEM_ARCHIVED = "ITEM_ARCHIVED", "Item archived"
    ITEM_RESTORED = "ITEM_RESTORED", "Item restored"
    UNIT_CREATED = "UNIT_CREATED", "Unit created"
    UNIT_UPDATED = "UNIT_UPDATED", "Unit updated"
    SETTINGS_UPDATED = "SETTINGS_UPDATED", "Settings updated"


class AuditTarget(models.TextChoices):
    USER = "accounts.User", "User"
    CATEGORY = "inventory.Category", "Category"
    CATALOG_ITEM = "inventory.CatalogItem", "Catalog item"
    EQUIPMENT_UNIT = "inventory.EquipmentUnit", "Equipment unit"
    BORROW_REQUEST = "borrowing.BorrowRequest", "Borrow request"
    LOAN = "borrowing.Loan", "Loan"
    RETURN_RECORD = "borrowing.ReturnRecord", "Return record"
    MAINTENANCE_RECORD = "inventory.MaintenanceRecord", "Maintenance record"
    SYSTEM_SETTING = "operations.SystemSetting", "System setting"


class SystemSetting(models.Model):
    id = models.SmallIntegerField(primary_key=True)
    max_loan_days = models.PositiveIntegerField()
    max_quantity_per_item = models.PositiveIntegerField()
    updated_at = models.DateTimeField()
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="settings_updates",
        null=True,
        blank=True,
    )

    class Meta:
        constraints: list[models.BaseConstraint] = [
            models.CheckConstraint(condition=models.Q(id=1), name="settings_singleton_id"),
            models.CheckConstraint(
                condition=models.Q(max_loan_days__gt=0, max_quantity_per_item__gt=0),
                name="settings_positive_limits",
            ),
        ]


class AuditLog(models.Model):
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="audit_logs",
        null=True,
        blank=True,
    )
    actor_kind = models.CharField(max_length=6, choices=AuditActorKind.choices)
    action = models.CharField(max_length=40, choices=AuditAction.choices)
    occurred_at = models.DateTimeField()
    target_model = models.CharField(max_length=64, choices=AuditTarget.choices)
    target_id = models.PositiveBigIntegerField()
    summary = models.TextField()

    class Meta:
        indexes: list[models.Index] = [
            models.Index(fields=["occurred_at"], name="audit_occurred_at_idx"),
            models.Index(fields=["action"], name="audit_action_idx"),
            models.Index(fields=["target_model", "target_id"], name="audit_target_idx"),
        ]
        constraints: list[models.BaseConstraint] = [
            models.CheckConstraint(
                condition=models.Q(actor_kind__in=AuditActorKind.values),
                name="audit_valid_actor_kind",
            ),
            models.CheckConstraint(
                condition=models.Q(action__in=AuditAction.values), name="audit_valid_action"
            ),
            models.CheckConstraint(
                condition=models.Q(target_model__in=AuditTarget.values), name="audit_valid_target"
            ),
            models.CheckConstraint(
                condition=models.Q(target_id__gt=0), name="audit_positive_target_id"
            ),
            models.CheckConstraint(
                condition=models.Q(summary__regex=r"\S"), name="audit_nonblank_summary"
            ),
            models.CheckConstraint(
                condition=models.Q(actor_kind=AuditActorKind.SYSTEM, actor__isnull=True)
                | models.Q(actor_kind=AuditActorKind.USER, actor__isnull=False),
                name="audit_actor_kind_matches_user",
            ),
        ]
