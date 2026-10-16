"""Explicit transactional operational changes shared with custom admin views."""

from django.core.exceptions import ImproperlyConfigured, PermissionDenied
from django.db import transaction
from django.utils import timezone

from accounts.models import User, UserRole
from operations.audit import write_audit
from operations.models import AuditAction, AuditTarget, SystemSetting
from operations.validation import LoanLimits, validate_loan_limits


def update_settings(actor_id: int, max_loan_days: int, max_quantity_per_item: int) -> SystemSetting:
    limits: LoanLimits = validate_loan_limits(max_loan_days, max_quantity_per_item)
    with transaction.atomic():
        actor: User = User.objects.select_for_update().get(pk=actor_id)
        if not actor.is_active or actor.role != UserRole.ADMIN:
            raise PermissionDenied(
                "Updating operational settings requires an active ADMIN account."
            )
        try:
            setting: SystemSetting = SystemSetting.objects.select_for_update().get(pk=1)
        except SystemSetting.DoesNotExist as error:
            raise ImproperlyConfigured(
                "SystemSetting row 1 is missing; restore the initialized singleton before changing limits."
            ) from error
        summary: str = (
            f"Maximum loan days: {setting.max_loan_days} -> {limits.max_loan_days}; "
            f"maximum quantity per item: {setting.max_quantity_per_item} -> {limits.max_quantity_per_item}."
        )
        setting.max_loan_days = limits.max_loan_days
        setting.max_quantity_per_item = limits.max_quantity_per_item
        setting.updated_by_id = actor_id
        setting.updated_at = timezone.now()
        setting.save(
            update_fields=["max_loan_days", "max_quantity_per_item", "updated_by", "updated_at"]
        )
        write_audit(
            actor_id, AuditAction.SETTINGS_UPDATED, AuditTarget.SYSTEM_SETTING, setting.pk, summary
        )
        return setting
