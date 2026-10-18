"""Category and catalog item business transitions with audit completeness."""

from django.core.exceptions import PermissionDenied, ValidationError
from django.db import IntegrityError, transaction
from psycopg.errors import UniqueViolation

from accounts.access import require_active_admin
from accounts.models import User
from inventory.models import CatalogItem, Category
from inventory.queries import has_transactional_history
from operations.audit import write_audit
from operations.locking import lock_catalog
from operations.models import AuditAction, AuditTarget


class CategoryArchiveConflict(Exception):
    """Raised when an administrator attempts to archive an already archived category."""


class ItemArchiveConflict(Exception):
    """Raised when an administrator attempts to archive an already archived item."""


class CategoryRestoreConflict(Exception):
    """Raised when an administrator attempts to restore an active category."""


class ItemRestoreConflict(Exception):
    """Raised when an administrator attempts to restore an active item."""


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
