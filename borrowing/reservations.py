"""Validate and lock complete reservations for cancellation and release."""

from dataclasses import dataclass

from django.core.exceptions import ValidationError

from borrowing.models import RequestItem, UnitAllocation
from inventory.models import CatalogItem, EquipmentUnit, UnitStatus
from operations.locking import lock_catalog, lock_units, require_atomic_transaction


class ReservationConflict(Exception):
    """An Approved request no longer has its complete, unreleased reservation."""


@dataclass(frozen=True)
class ReservedUnits:
    units: tuple[EquipmentUnit, ...]
    allocations: tuple[UnitAllocation, ...]


def lock_reserved_units(request_id: int) -> ReservedUnits:
    """Call after locking borrower/request/loan; preserve catalog, unit, allocation order.

    Archived catalog records remain valid for existing reservations. Re-read the
    allocation set after unit locks so changed relationships cannot be issued or freed.
    """
    require_atomic_transaction()
    items: tuple[RequestItem, ...] = tuple(
        RequestItem.objects.select_for_update().filter(request_id=request_id).order_by("pk")
    )
    allocations: tuple[UnitAllocation, ...] = tuple(
        UnitAllocation.objects.filter(request_item__request_id=request_id).order_by("pk")
    )
    if not items or not allocations:
        raise ReservationConflict("The Approved request has no complete reservation.")
    try:
        lock_catalog(tuple(item.catalog_item_id for item in items))
    except (CatalogItem.DoesNotExist, ValidationError) as error:
        raise ReservationConflict("The reserved equipment changed; refresh the request.") from error

    item_by_id: dict[int, RequestItem] = {item.pk: item for item in items}
    counts: dict[int, int] = {}
    for allocation in allocations:
        if (
            allocation.released_at is not None
            or allocation.cancelled_at is not None
            or allocation.ended_at is not None
        ):
            raise ReservationConflict("A reservation has already been released or ended.")
        counts[allocation.request_item_id] = counts.get(allocation.request_item_id, 0) + 1
    unit_ids: tuple[int, ...] = tuple(allocation.unit_id for allocation in allocations)
    if len(unit_ids) != len(set(unit_ids)) or any(
        counts.get(item.pk, 0) != item.quantity for item in items
    ):
        raise ReservationConflict("The Approved request does not have its complete reservation.")
    try:
        units: tuple[EquipmentUnit, ...] = lock_units(unit_ids)
    except (EquipmentUnit.DoesNotExist, ValidationError) as error:
        raise ReservationConflict(
            "A reserved equipment unit changed; refresh the request."
        ) from error
    unit_by_id: dict[int, EquipmentUnit] = {unit.pk: unit for unit in units}
    for allocation in allocations:
        unit: EquipmentUnit = unit_by_id[allocation.unit_id]
        if (
            unit.status != UnitStatus.RESERVED
            or unit.catalog_item_id != item_by_id[allocation.request_item_id].catalog_item_id
        ):
            raise ReservationConflict(
                "A reserved unit has an inconsistent item or inventory status."
            )

    locked_allocations: tuple[UnitAllocation, ...] = tuple(
        UnitAllocation.objects.select_for_update()
        .filter(request_item__request_id=request_id)
        .order_by("pk")
    )
    if tuple(
        (row.pk, row.request_item_id, row.unit_id, row.released_at, row.cancelled_at, row.ended_at)
        for row in locked_allocations
    ) != tuple(
        (row.pk, row.request_item_id, row.unit_id, row.released_at, row.cancelled_at, row.ended_at)
        for row in allocations
    ):
        raise ReservationConflict("A reservation changed while the action was in progress.")
    if UnitAllocation.objects.filter(
        pk__in=[allocation.pk for allocation in locked_allocations], loan_unit__isnull=False
    ).exists():
        raise ReservationConflict("A reserved allocation already belongs to an issued loan.")
    return ReservedUnits(units=units, allocations=locked_allocations)
