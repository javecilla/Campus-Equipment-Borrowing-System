"""Top up existing active catalog items through audited unit registration."""

from datetime import date

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from accounts.access import require_active_admin
from accounts.models import User
from inventory.models import CatalogItem, EquipmentUnit, UnitCondition
from inventory.services import create_equipment_unit


@transaction.atomic
def seed_demo_units(admin_username: str, quantity_per_item: int, acquired_on: date) -> int:
    """Ensure a minimum total stock count; preserve every existing unit and photo."""
    if quantity_per_item < 1:
        raise ValidationError("Quantity per item must be at least 1.")
    if acquired_on > timezone.localdate():
        raise ValidationError("Acquisition date cannot be in the future.")
    try:
        admin: User = User.objects.select_for_update().get(username=admin_username)
    except User.DoesNotExist as error:
        raise ValidationError(
            f'Administrator "{admin_username}" does not exist. Seed accounts first.'
        ) from error
    require_active_admin(admin)
    items: tuple[CatalogItem, ...] = tuple(
        CatalogItem.objects.filter(is_archived=False, category__is_archived=False).order_by("pk")
    )
    if not items:
        raise ValidationError(
            "No active equipment catalog items exist. Add or restore catalog records first."
        )
    created: int = 0
    for item in items:
        existing: int = EquipmentUnit.objects.filter(catalog_item=item).count()
        for number in range(existing + 1, quantity_per_item + 1):
            create_equipment_unit(
                admin.pk,
                item.pk,
                f"DEMO-{item.pk:04d}-{number:03d}",
                UnitCondition.GOOD,
                acquired_on,
                f"Demonstration stock for {item.name}; inspect and return all supplied accessories after use.",
                None,
            )
            created += 1
    return created
