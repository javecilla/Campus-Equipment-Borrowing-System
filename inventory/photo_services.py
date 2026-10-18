"""Explicit photo changes with audited database writes and filesystem cleanup."""

from functools import partial
from uuid import uuid4

from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.db import transaction

from inventory.models import CatalogItem
from inventory.photos import prepare_equipment_photo
from inventory.services import _require_active_admin, create_catalog_item
from operations.audit import write_audit
from operations.locking import lock_catalog
from operations.models import AuditAction, AuditTarget


class ItemPhotoConflict(Exception):
    """The item no longer has an uploaded photo to remove."""


def _record_photo(actor_id: int, item_id: int, stored_name: str) -> CatalogItem:
    """Assign and audit a stored image while the caller holds the item's transaction/lock."""
    item: CatalogItem = CatalogItem.objects.get(pk=item_id)
    item.photo = stored_name
    item.save(update_fields=["photo", "updated_at"])
    write_audit(
        actor_id,
        AuditAction.ITEM_UPDATED,
        AuditTarget.CATALOG_ITEM,
        item.pk,
        "Equipment photo uploaded or replaced.",
    )
    return item


def create_catalog_item_with_photo(
    actor_id: int, category_id: int, name: str, description: str, content: bytes
) -> CatalogItem:
    """Create the item, validated photo and both audit records as one complete action."""
    try:
        prepared: bytes = prepare_equipment_photo(content)
    except ValidationError as error:
        raise ValidationError({"photo": error.messages}) from error
    stored_name: str | None = None
    try:
        with transaction.atomic(durable=True):
            item: CatalogItem = create_catalog_item(actor_id, category_id, name, description)
            stored_name = default_storage.save(
                f"equipment/{uuid4().hex}.webp", ContentFile(prepared)
            )
            item = _record_photo(actor_id, item.pk, stored_name)
    except BaseException:
        if stored_name is not None:
            default_storage.delete(stored_name)
        raise
    return item


def replace_item_photo(actor_id: int, item_id: int, content: bytes) -> CatalogItem:
    """Commit the new reference/audit together; clean a new file if its database write fails.

    A durable transaction prevents a caller rolling back an enclosing transaction
    after this function has successfully stored a file. Old files are deleted only
    after commit, outside the new-file rollback handler.
    """
    prepared: bytes = prepare_equipment_photo(content)
    stored_name: str | None = None
    try:
        with transaction.atomic(durable=True):
            _require_active_admin(actor_id)
            item: CatalogItem = lock_catalog((item_id,)).items[0]
            previous_name: str = item.photo.name
            stored_name = default_storage.save(
                f"equipment/{uuid4().hex}.webp", ContentFile(prepared)
            )
            item = _record_photo(actor_id, item.pk, stored_name)
    except BaseException:
        # Cleanup is not recovery: always propagate the original transaction failure.
        if stored_name is not None:
            default_storage.delete(stored_name)
        raise
    if previous_name:
        transaction.on_commit(partial(default_storage.delete, previous_name))
    return item


def remove_item_photo(actor_id: int, item_id: int) -> CatalogItem:
    """Remove the reference and audit atomically before deleting the old uploaded file."""
    with transaction.atomic(durable=True):
        _require_active_admin(actor_id)
        item: CatalogItem = lock_catalog((item_id,)).items[0]
        previous_name: str = item.photo.name
        if not previous_name:
            raise ItemPhotoConflict("This equipment item no longer has an uploaded photo.")
        item.photo = ""
        item.save(update_fields=["photo", "updated_at"])
        write_audit(
            actor_id,
            AuditAction.ITEM_UPDATED,
            AuditTarget.CATALOG_ITEM,
            item.pk,
            "Equipment photo removed; default equipment image restored.",
        )
    transaction.on_commit(partial(default_storage.delete, previous_name))
    return item
