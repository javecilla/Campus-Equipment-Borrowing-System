"""Category and catalog item business transitions with audit completeness."""

from datetime import date

from django.core.exceptions import PermissionDenied, ValidationError
from django.db import IntegrityError, transaction
from django.utils import timezone
from psycopg.errors import UniqueViolation

from accounts.access import require_active_admin
from accounts.models import User
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
from inventory.queries import (
    has_transactional_history,
    has_unit_transactional_history,
)
from operations.audit import write_audit
from operations.locking import lock_catalog, lock_units
from operations.models import AuditAction, AuditTarget


class CategoryArchiveConflict(Exception):
    """Raised when an administrator attempts to archive an already archived category."""


class ItemArchiveConflict(Exception):
    """Raised when an administrator attempts to archive an already archived item."""


class CategoryRestoreConflict(Exception):
    """Raised when an administrator attempts to restore an active category."""


class ItemRestoreConflict(Exception):
    """Raised when an administrator attempts to restore an active item."""


class MaintenanceConflict(Exception):
    """The unit or maintenance record no longer permits the requested action."""


def _require_active_admin(actor_id: int) -> User:
    try:
        actor: User = User.objects.select_for_update().get(pk=actor_id)
    except User.DoesNotExist as error:
        raise PermissionDenied("The performing administrator account does not exist.") from error
    return require_active_admin(actor)


def _save_category(category: Category) -> None:
    """Translate only the known concurrent name conflict after rolling back its savepoint."""
    try:
        with transaction.atomic():
            category.full_clean(validate_unique=False, validate_constraints=False)
            category.save()
    except IntegrityError as error:
        cause: BaseException | None = error.__cause__
        if isinstance(cause, UniqueViolation) and cause.diag.constraint_name in {
            "category_name_ci_unique",
            "inventory_category_name_key",
        }:
            raise ValidationError("A category with this name already exists.") from error
        raise


def create_category(actor_id: int, name: str, description: str) -> Category:
    """Create a new category and record the business action in the same transaction."""
    with transaction.atomic():
        _require_active_admin(actor_id)
        clean_name: str = name.strip()
        if not clean_name:
            raise ValidationError("Category name cannot be blank.")
        if Category.objects.filter(name__iexact=clean_name).exists():
            raise ValidationError("A category with this name already exists.")
        clean_description: str = description.strip()
        category: Category = Category(
            name=clean_name,
            description=clean_description,
            is_archived=False,
        )
        _save_category(category)
        write_audit(
            actor_id=actor_id,
            action=AuditAction.CATEGORY_CREATED,
            target_model=AuditTarget.CATEGORY,
            target_id=category.pk,
            summary=f"Created category {category.name}.",
        )
        return category


def update_category(actor_id: int, category_id: int, name: str, description: str) -> Category:
    """Update category metadata under row locks and audit the change."""
    with transaction.atomic():
        _require_active_admin(actor_id)
        clean_name: str = name.strip()
        if not clean_name:
            raise ValidationError("Category name cannot be blank.")
        if Category.objects.filter(name__iexact=clean_name).exclude(pk=category_id).exists():
            raise ValidationError("A category with this name already exists.")
        category: Category = Category.objects.select_for_update().get(pk=category_id)
        clean_description: str = description.strip()
        category.name = clean_name
        category.description = clean_description
        _save_category(category)
        write_audit(
            actor_id=actor_id,
            action=AuditAction.CATEGORY_UPDATED,
            target_model=AuditTarget.CATEGORY,
            target_id=category.pk,
            summary=f"Updated category {category.name}.",
        )
        return category


def archive_category(actor_id: int, category_id: int) -> Category:
    """Archive a category without deleting referenced catalog or workflow records."""
    with transaction.atomic():
        _require_active_admin(actor_id)
        category: Category = Category.objects.select_for_update().get(pk=category_id)
        if category.is_archived:
            raise CategoryArchiveConflict(f'Category "{category.name}" is already archived.')
        category.is_archived = True
        category.save(update_fields=["is_archived", "updated_at"])
        write_audit(
            actor_id=actor_id,
            action=AuditAction.CATEGORY_ARCHIVED,
            target_model=AuditTarget.CATEGORY,
            target_id=category.pk,
            summary=f"Archived category {category.name}.",
        )
        return category


def restore_category(actor_id: int, category_id: int) -> Category:
    """Restore only the category; preserve each child's independent archive status."""
    with transaction.atomic():
        _require_active_admin(actor_id)
        category: Category = Category.objects.select_for_update().get(pk=category_id)
        if not category.is_archived:
            raise CategoryRestoreConflict(f'Category "{category.name}" is already active.')
        category.is_archived = False
        category.save(update_fields=["is_archived", "updated_at"])
        write_audit(
            actor_id=actor_id,
            action=AuditAction.CATEGORY_RESTORED,
            target_model=AuditTarget.CATEGORY,
            target_id=category.pk,
            summary=f"Restored category {category.name}; individual item archive statuses preserved.",
        )
        return category


def create_catalog_item(
    actor_id: int, category_id: int, name: str, description: str
) -> CatalogItem:
    """Create a new catalog item under an active category and audit the action."""
    with transaction.atomic():
        _require_active_admin(actor_id)
        category: Category = Category.objects.select_for_update().get(pk=category_id)
        if category.is_archived:
            raise ValidationError("Cannot create an equipment item under an archived category.")
        clean_name: str = name.strip()
        if not clean_name:
            raise ValidationError("Item name cannot be blank.")
        clean_description: str = description.strip()
        if not clean_description:
            raise ValidationError("Item description cannot be blank.")
        item: CatalogItem = CatalogItem(
            category=category,
            name=clean_name,
            description=clean_description,
            is_archived=False,
        )
        item.full_clean()
        item.save()
        write_audit(
            actor_id=actor_id,
            action=AuditAction.ITEM_CREATED,
            target_model=AuditTarget.CATALOG_ITEM,
            target_id=item.pk,
            summary=f"Created equipment item {item.name} under category {category.name}.",
        )
        return item


def update_catalog_item(
    actor_id: int,
    item_id: int,
    name: str,
    description: str,
    category_id: int | None,
) -> CatalogItem:
    """Update catalog item fields; category change is blocked once transactional history exists."""
    with transaction.atomic():
        _require_active_admin(actor_id)
        clean_name: str = name.strip()
        if not clean_name:
            raise ValidationError("Item name cannot be blank.")
        clean_description: str = description.strip()
        if not clean_description:
            raise ValidationError("Item description cannot be blank.")
        original_category_id: int = CatalogItem.objects.values_list("category_id", flat=True).get(
            pk=item_id
        )
        category_ids: tuple[int, ...] = tuple(
            sorted(
                {original_category_id, category_id}
                if category_id is not None
                else {original_category_id}
            )
        )
        categories: dict[int, Category] = {
            category.pk: category
            for category in Category.objects.select_for_update()
            .filter(pk__in=category_ids)
            .order_by("pk")
        }
        if category_id is not None and category_id not in categories:
            raise Category.DoesNotExist("The selected category does not exist.")
        item: CatalogItem = CatalogItem.objects.select_for_update().get(pk=item_id)
        if item.category_id != original_category_id:
            raise ValidationError(
                "The item's category changed during editing; reload the form and try again."
            )
        update_fields: list[str] = ["name", "description", "updated_at"]
        item.name = clean_name
        item.description = clean_description

        if category_id is not None and category_id != item.category_id:
            if has_transactional_history(item_id):
                raise ValidationError(
                    "A catalog item's category cannot change after transactional history exists."
                )
            new_category: Category = categories[category_id]
            if new_category.is_archived:
                raise ValidationError("Cannot assign an equipment item to an archived category.")
            item.category = new_category
            update_fields.append("category")

        item.full_clean()
        item.save(update_fields=update_fields)
        write_audit(
            actor_id=actor_id,
            action=AuditAction.ITEM_UPDATED,
            target_model=AuditTarget.CATALOG_ITEM,
            target_id=item.pk,
            summary=f"Updated equipment item {item.name}.",
        )
        return item


def archive_catalog_item(actor_id: int, item_id: int) -> CatalogItem:
    """Archive a catalog item to block new requests/approvals while preserving existing workflows."""
    with transaction.atomic():
        _require_active_admin(actor_id)
        item: CatalogItem = lock_catalog((item_id,)).items[0]
        if item.is_archived:
            raise ItemArchiveConflict(f'Equipment item "{item.name}" is already archived.')
        item.is_archived = True
        item.save(update_fields=["is_archived", "updated_at"])
        write_audit(
            actor_id=actor_id,
            action=AuditAction.ITEM_ARCHIVED,
            target_model=AuditTarget.CATALOG_ITEM,
            target_id=item.pk,
            summary=f"Archived equipment item {item.name}.",
        )
        return item


def restore_catalog_item(actor_id: int, item_id: int) -> CatalogItem:
    """Restore the item's archive flag without changing its category or physical units."""
    with transaction.atomic():
        _require_active_admin(actor_id)
        item: CatalogItem = lock_catalog((item_id,)).items[0]
        if not item.is_archived:
            raise ItemRestoreConflict(f'Equipment item "{item.name}" is already active.')
        item.is_archived = False
        item.save(update_fields=["is_archived", "updated_at"])
        write_audit(
            actor_id=actor_id,
            action=AuditAction.ITEM_RESTORED,
            target_model=AuditTarget.CATALOG_ITEM,
            target_id=item.pk,
            summary=f"Restored equipment item {item.name}; category and unit statuses preserved.",
        )
        return item


def _save_equipment_unit(unit: EquipmentUnit) -> None:
    """Translate unique asset code conflicts after rolling back its savepoint."""
    try:
        with transaction.atomic():
            unit.full_clean(validate_unique=False, validate_constraints=False)
            unit.save()
    except IntegrityError as error:
        cause: BaseException | None = error.__cause__
        if isinstance(cause, UniqueViolation) and cause.diag.constraint_name in {
            "unit_asset_code_ci_unique",
            "inventory_equipmentunit_asset_code_key",
        }:
            raise ValidationError("A physical unit with this asset code already exists.") from error
        raise


def create_equipment_unit(
    actor_id: int,
    catalog_item_id: int,
    asset_code: str,
    condition: str,
    acquired_on: date,
    internal_notes: str,
    maintenance_problem: str | None,
) -> EquipmentUnit:
    """Register a new physical unit and audit the creation.

    If condition is DAMAGED, requires nonblank maintenance_problem and
    creates initial open maintenance atomically.
    """
    with transaction.atomic():
        _require_active_admin(actor_id)
        locked = lock_catalog((catalog_item_id,))
        item: CatalogItem = locked.items[0]
        if item.is_archived:
            raise ValidationError("Cannot register a physical unit for an archived equipment item.")
        if item.category.is_archived:
            raise ValidationError("Cannot register a physical unit under an archived category.")

        clean_code: str = asset_code.strip()
        if not clean_code:
            raise ValidationError("Asset code cannot be blank.")
        if EquipmentUnit.objects.filter(asset_code__iexact=clean_code).exists():
            raise ValidationError("A physical unit with this asset code already exists.")

        if condition not in UnitCondition.values:
            raise ValidationError(f"Invalid condition '{condition}'.")

        if acquired_on > timezone.localdate():
            raise ValidationError("Acquisition date cannot be in the future.")

        clean_notes: str = internal_notes.strip()
        clean_problem: str = (maintenance_problem or "").strip()

        if condition == UnitCondition.DAMAGED:
            if not clean_problem:
                raise ValidationError(
                    "A maintenance problem description is required when registering a damaged unit."
                )
            status: str = UnitStatus.MAINTENANCE
        else:
            status = UnitStatus.AVAILABLE

        unit: EquipmentUnit = EquipmentUnit(
            catalog_item=item,
            asset_code=clean_code,
            condition=condition,
            acquired_on=acquired_on,
            status=status,
            internal_notes=clean_notes,
        )
        unit.full_clean()
        _save_equipment_unit(unit)

        write_audit(
            actor_id=actor_id,
            action=AuditAction.UNIT_CREATED,
            target_model=AuditTarget.EQUIPMENT_UNIT,
            target_id=unit.pk,
            summary=f"Registered physical unit {unit.asset_code} ({unit.get_condition_display()}) for {item.name}.",
        )

        if condition == UnitCondition.DAMAGED:
            maintenance: MaintenanceRecord = MaintenanceRecord(
                unit=unit,
                source_return=None,
                problem=clean_problem,
                action="",
                opened_at=timezone.now(),
                opened_by_id=actor_id,
                status=MaintenanceStatus.OPEN,
                closed_at=None,
                closed_by=None,
                outcome=None,
            )
            maintenance.full_clean()
            maintenance.save()
            write_audit(
                actor_id=actor_id,
                action=AuditAction.MAINTENANCE_OPENED,
                target_model=AuditTarget.MAINTENANCE_RECORD,
                target_id=maintenance.pk,
                summary=f"Opened initial maintenance for unit {unit.asset_code}: {clean_problem}.",
            )

        return unit


def update_equipment_unit(
    actor_id: int,
    unit_id: int,
    internal_notes: str,
    asset_code: str | None,
    catalog_item_id: int | None,
    acquired_on: date | None,
) -> EquipmentUnit:
    """Update physical unit metadata under row locks and audit the change.

    If the unit has transactional history (allocations or maintenance),
    asset_code, catalog_item, and acquired_on cannot be altered.
    Condition and status can never be modified through generic editing.
    """
    with transaction.atomic():
        _require_active_admin(actor_id)
        unit: EquipmentUnit = lock_units((unit_id,))[0]
        has_history: bool = has_unit_transactional_history(unit_id)
        clean_notes: str = internal_notes.strip()

        if has_history:
            if asset_code is not None and asset_code.strip() != unit.asset_code:
                raise ValidationError(
                    "Asset code cannot be changed after transactional history exists."
                )
            if catalog_item_id is not None and catalog_item_id != unit.catalog_item_id:
                raise ValidationError(
                    "Catalog item cannot be changed after transactional history exists."
                )
            if acquired_on is not None and acquired_on != unit.acquired_on:
                raise ValidationError(
                    "Acquisition date cannot be changed after transactional history exists."
                )

            unit.internal_notes = clean_notes
            unit.full_clean()
            unit.save(update_fields=["internal_notes", "updated_at"])
            summary: str = f"Updated internal notes for physical unit {unit.asset_code}."
        else:
            if asset_code is None:
                raise ValidationError("Asset code is required.")
            clean_code: str = asset_code.strip()
            if not clean_code:
                raise ValidationError("Asset code cannot be blank.")
            if (
                EquipmentUnit.objects.filter(asset_code__iexact=clean_code)
                .exclude(pk=unit_id)
                .exists()
            ):
                raise ValidationError("A physical unit with this asset code already exists.")

            if acquired_on is None:
                raise ValidationError("Acquisition date is required.")
            if acquired_on > timezone.localdate():
                raise ValidationError("Acquisition date cannot be in the future.")

            if catalog_item_id is None:
                raise ValidationError("Catalog item is required.")

            if catalog_item_id != unit.catalog_item_id:
                locked = lock_catalog((catalog_item_id,))
                new_item: CatalogItem = locked.items[0]
                if new_item.is_archived:
                    raise ValidationError(
                        "Cannot assign a physical unit to an archived equipment item."
                    )
                if new_item.category.is_archived:
                    raise ValidationError(
                        "Cannot assign a physical unit under an archived category."
                    )
                unit.catalog_item = new_item

            unit.asset_code = clean_code
            unit.acquired_on = acquired_on
            unit.internal_notes = clean_notes
            unit.full_clean()
            _save_equipment_unit(unit)
            summary = f"Updated physical unit {unit.asset_code}."

        write_audit(
            actor_id=actor_id,
            action=AuditAction.UNIT_UPDATED,
            target_model=AuditTarget.EQUIPMENT_UNIT,
            target_id=unit.pk,
            summary=summary,
        )
        return unit


def open_maintenance(
    actor_id: int,
    unit_id: int,
    problem: str,
) -> MaintenanceRecord:
    """Open manual maintenance on an Available unit and audit it atomically.

    Damaged-return maintenance belongs to the complete return transaction, not this
    manual action; a return identifier must never bypass unit eligibility.
    """
    with transaction.atomic():
        _require_active_admin(actor_id)
        clean_problem: str = problem.strip()
        if not clean_problem:
            raise ValidationError("Problem description is required to open maintenance.")

        unit: EquipmentUnit = lock_units((unit_id,))[0]

        if unit.status == UnitStatus.RESERVED:
            raise MaintenanceConflict("Cannot open maintenance on a reserved physical unit.")
        if unit.status == UnitStatus.ISSUED:
            raise MaintenanceConflict("Cannot open maintenance on an issued physical unit.")
        if unit.status == UnitStatus.MAINTENANCE:
            raise MaintenanceConflict(
                "Cannot open maintenance on a physical unit that is already in maintenance."
            )
        if unit.status == UnitStatus.RETIRED:
            raise MaintenanceConflict("Cannot open maintenance on a retired physical unit.")
        if unit.status != UnitStatus.AVAILABLE:
            raise MaintenanceConflict(
                f"Cannot open maintenance on a physical unit with status {unit.get_status_display()}."
            )

        if MaintenanceRecord.objects.filter(unit=unit, status=MaintenanceStatus.OPEN).exists():
            raise MaintenanceConflict(
                f"Physical unit {unit.asset_code} already has an active open maintenance record."
            )

        unit.status = UnitStatus.MAINTENANCE
        unit.full_clean()
        unit.save(update_fields=["status", "updated_at"])

        maintenance: MaintenanceRecord = MaintenanceRecord(
            unit=unit,
            source_return=None,
            problem=clean_problem,
            action="",
            opened_at=timezone.now(),
            opened_by_id=actor_id,
            status=MaintenanceStatus.OPEN,
            closed_at=None,
            closed_by=None,
            outcome=None,
        )
        maintenance.full_clean()
        maintenance.save()

        write_audit(
            actor_id=actor_id,
            action=AuditAction.MAINTENANCE_OPENED,
            target_model=AuditTarget.MAINTENANCE_RECORD,
            target_id=maintenance.pk,
            summary=f"Opened maintenance for physical unit {unit.asset_code}: {clean_problem}.",
        )
        return maintenance


def close_maintenance(
    actor_id: int,
    maintenance_id: int,
    action: str,
    outcome: str,
    repaired_condition: str | None,
) -> MaintenanceRecord:
    """Close an open maintenance record under row locks, reconcile unit status, and audit.

    AVAILABLE outcome returns the repaired unit to serviceable inventory;
    RETIRED outcome retains the unit as unavailable per BR-10.
    """
    with transaction.atomic():
        _require_active_admin(actor_id)
        try:
            maintenance_unit_id: int = MaintenanceRecord.objects.values_list(
                "unit_id", flat=True
            ).get(pk=maintenance_id)
        except MaintenanceRecord.DoesNotExist as error:
            raise ValidationError(
                f"Maintenance record with ID {maintenance_id} does not exist."
            ) from error

        unit: EquipmentUnit = lock_units((maintenance_unit_id,))[0]
        try:
            maintenance: MaintenanceRecord = MaintenanceRecord.objects.select_for_update().get(
                pk=maintenance_id, unit_id=unit.pk
            )
        except MaintenanceRecord.DoesNotExist as error:
            raise MaintenanceConflict(
                "The maintenance record changed; refresh the page before retrying."
            ) from error

        if maintenance.status != MaintenanceStatus.OPEN:
            raise MaintenanceConflict("This maintenance record is already closed.")
        if unit.status != UnitStatus.MAINTENANCE:
            raise MaintenanceConflict(
                f"Physical unit {unit.asset_code} is not currently in maintenance."
            )

        clean_action: str = action.strip()
        if not clean_action:
            raise ValidationError("Action taken is required when closing maintenance.")

        if outcome not in MaintenanceOutcome.values:
            raise ValidationError("Invalid maintenance outcome. Must be Available or Retired.")

        if outcome == MaintenanceOutcome.AVAILABLE:
            unit.status = UnitStatus.AVAILABLE
            if repaired_condition:
                if repaired_condition not in (UnitCondition.GOOD, UnitCondition.FAIR):
                    raise ValidationError("Repaired physical unit condition must be Good or Fair.")
                unit.condition = repaired_condition
            elif unit.condition == UnitCondition.DAMAGED:
                unit.condition = UnitCondition.GOOD
            unit.full_clean()
            unit.save(update_fields=["status", "condition", "updated_at"])
        elif outcome == MaintenanceOutcome.RETIRED:
            unit.status = UnitStatus.RETIRED
            unit.full_clean()
            unit.save(update_fields=["status", "updated_at"])

        maintenance.action = clean_action
        maintenance.status = MaintenanceStatus.CLOSED
        maintenance.outcome = outcome
        maintenance.closed_at = timezone.now()
        maintenance.closed_by_id = actor_id
        maintenance.full_clean()
        maintenance.save()

        outcome_label: str = maintenance.get_outcome_display()
        write_audit(
            actor_id=actor_id,
            action=AuditAction.MAINTENANCE_CLOSED,
            target_model=AuditTarget.MAINTENANCE_RECORD,
            target_id=maintenance.pk,
            summary=f"Closed maintenance for physical unit {unit.asset_code} with outcome {outcome_label}: {clean_action}.",
        )
        return maintenance
