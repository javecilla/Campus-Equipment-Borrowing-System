"""Append validated audit entries inside the caller's business transaction."""

from collections.abc import Mapping
from types import MappingProxyType

from django.apps import apps
from django.core.exceptions import PermissionDenied, ValidationError
from django.db.models import Model
from django.utils import timezone
from django.utils.html import strip_tags

from accounts.models import User
from operations.locking import require_atomic_transaction
from operations.models import AuditAction, AuditActorKind, AuditLog, AuditTarget

ACTION_TARGETS: Mapping[AuditAction, AuditTarget] = MappingProxyType(
    {
        AuditAction.REQUEST_APPROVED: AuditTarget.BORROW_REQUEST,
        AuditAction.REQUEST_REJECTED: AuditTarget.BORROW_REQUEST,
        AuditAction.REQUEST_CANCELLED: AuditTarget.BORROW_REQUEST,
        AuditAction.DUE_DATE_REVISED: AuditTarget.BORROW_REQUEST,
        AuditAction.LOAN_RELEASED: AuditTarget.LOAN,
        AuditAction.UNIT_RETURNED: AuditTarget.RETURN_RECORD,
        AuditAction.MAINTENANCE_OPENED: AuditTarget.MAINTENANCE_RECORD,
        AuditAction.MAINTENANCE_CLOSED: AuditTarget.MAINTENANCE_RECORD,
        AuditAction.ACCOUNT_CREATED: AuditTarget.USER,
        AuditAction.ACCOUNT_UPDATED: AuditTarget.USER,
        AuditAction.ACCOUNT_ACTIVATED: AuditTarget.USER,
        AuditAction.ACCOUNT_DEACTIVATED: AuditTarget.USER,
        AuditAction.CATEGORY_CREATED: AuditTarget.CATEGORY,
        AuditAction.CATEGORY_UPDATED: AuditTarget.CATEGORY,
        AuditAction.CATEGORY_ARCHIVED: AuditTarget.CATEGORY,
        AuditAction.CATEGORY_RESTORED: AuditTarget.CATEGORY,
        AuditAction.ITEM_CREATED: AuditTarget.CATALOG_ITEM,
        AuditAction.ITEM_UPDATED: AuditTarget.CATALOG_ITEM,
        AuditAction.ITEM_ARCHIVED: AuditTarget.CATALOG_ITEM,
        AuditAction.ITEM_RESTORED: AuditTarget.CATALOG_ITEM,
        AuditAction.UNIT_CREATED: AuditTarget.EQUIPMENT_UNIT,
        AuditAction.UNIT_UPDATED: AuditTarget.EQUIPMENT_UNIT,
        AuditAction.SETTINGS_UPDATED: AuditTarget.SYSTEM_SETTING,
    }
)


def write_audit(
    actor_id: int, action: AuditAction, target_model: AuditTarget, target_id: int, summary: str
) -> AuditLog:
    """The calling service owns action authorization and supplies no secrets/contact data.

    Actor and target reads acquire no new locks after the caller's business locks.
    System initialization uses historical models in its atomic data migration.
    """
    require_atomic_transaction()
    if not isinstance(action, AuditAction) or action not in ACTION_TARGETS:
        raise ValidationError(
            "Audit action must be an approved user business action; initialization is migration-only."
        )
    if not isinstance(target_model, AuditTarget) or ACTION_TARGETS[action] != target_model:
        raise ValidationError("Audit target model does not match the business action.")
    if type(target_id) is not int or target_id < 1:
        raise ValidationError("Audit target ID must be a positive integer.")
    actor: User = User.objects.get(pk=actor_id)
    if not actor.is_active:
        raise PermissionDenied("Inactive accounts cannot record business actions.")
    target_class: type[Model] = apps.get_model(target_model)
    if not target_class._default_manager.filter(pk=target_id).exists():
        raise ValidationError(f"Audit target {target_model} with ID {target_id} does not exist.")
    sanitized_summary: str = " ".join(strip_tags(summary).split())
    if not sanitized_summary:
        raise ValidationError(
            "Audit summary must contain a nonblank description without HTML markup."
        )
    return AuditLog.objects.create(
        actor_id=actor_id,
        actor_kind=AuditActorKind.USER,
        action=action,
        occurred_at=timezone.now(),
        target_model=target_model,
        target_id=target_id,
        summary=sanitized_summary,
    )
