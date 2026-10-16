"""One PostgreSQL lock order for callers inside an explicit atomic transaction.

Borrowing services acquire borrower, request, existing loan, categories, catalog
items, then units. Every collection is locked in ascending primary-key order.
Lock allocation/loan-unit rows only after their parents and units. Maintenance
starts with units and must never subsequently acquire borrowing-parent locks.
Callers enforce permissions, eligibility, quantities, and workflow transitions
using the returned authoritative rows; these helpers never change statuses.
"""

from dataclasses import dataclass

from django.core.exceptions import ValidationError
from django.db import connection
from django.db.transaction import TransactionManagementError

from accounts.models import User
from borrowing.models import BorrowRequest, Loan
from inventory.models import CatalogItem, Category, EquipmentUnit, UnitStatus


@dataclass(frozen=True)
class LockedRequest:
    borrower: User
    request: BorrowRequest
    loan: Loan | None


@dataclass(frozen=True)
class LockedCatalog:
    categories: tuple[Category, ...]
    items: tuple[CatalogItem, ...]


def require_atomic_transaction() -> None:
    if not connection.in_atomic_block:
        raise TransactionManagementError(
            "Workflow locks and audit writes require an enclosing transaction.atomic()."
        )


def ordered_ids(identifiers: tuple[int, ...]) -> tuple[int, ...]:
    if not identifiers or any(
        type(identifier) is not int or identifier < 1 for identifier in identifiers
    ):
        raise ValidationError("Lock targets must be a nonempty collection of positive integer IDs.")
    return tuple(sorted(set(identifiers)))


def lock_borrower(owner_id: int) -> User:
    require_atomic_transaction()
    return User.objects.select_for_update().get(pk=owner_id)


def lock_request(owner_id: int, request_id: int) -> LockedRequest:
    require_atomic_transaction()
    borrower: User = lock_borrower(owner_id)
    request: BorrowRequest = BorrowRequest.objects.select_for_update().get(
        pk=request_id, owner_id=owner_id
    )
    loan: Loan | None = Loan.objects.select_for_update().filter(request_id=request_id).first()
    return LockedRequest(borrower=borrower, request=request, loan=loan)


def lock_catalog(catalog_item_ids: tuple[int, ...]) -> LockedCatalog:
    require_atomic_transaction()
    identifiers: tuple[int, ...] = ordered_ids(catalog_item_ids)
    membership: tuple[tuple[int, int], ...] = tuple(
        CatalogItem.objects.filter(pk__in=identifiers)
        .order_by("pk")
        .values_list("pk", "category_id")
    )
    if tuple(item_id for item_id, category_id in membership) != identifiers:
        raise CatalogItem.DoesNotExist(
            f"Cannot lock catalog items {identifiers}: at least one ID does not exist."
        )
    category_ids: tuple[int, ...] = tuple(
        sorted({category_id for item_id, category_id in membership})
    )
    categories: tuple[Category, ...] = tuple(
        Category.objects.select_for_update().filter(pk__in=category_ids).order_by("pk")
    )
    items: tuple[CatalogItem, ...] = tuple(
        CatalogItem.objects.select_for_update().filter(pk__in=identifiers).order_by("pk")
    )
    if tuple((item.pk, item.category_id) for item in items) != membership:
        raise ValidationError(
            "Catalog membership changed while acquiring locks; no workflow change can be committed."
        )
    return LockedCatalog(categories=categories, items=items)


def lock_units(unit_ids: tuple[int, ...]) -> tuple[EquipmentUnit, ...]:
    require_atomic_transaction()
    identifiers: tuple[int, ...] = ordered_ids(unit_ids)
    units: tuple[EquipmentUnit, ...] = tuple(
        EquipmentUnit.objects.select_for_update().filter(pk__in=identifiers).order_by("pk")
    )
    if tuple(unit.pk for unit in units) != identifiers:
        raise EquipmentUnit.DoesNotExist(
            f"Cannot lock units {identifiers}: at least one ID does not exist."
        )
    return units


def lock_available_units(catalog_item_ids: tuple[int, ...]) -> tuple[EquipmentUnit, ...]:
    """Lock candidates together so multi-item selection never reverses unit order."""
    require_atomic_transaction()
    identifiers: tuple[int, ...] = ordered_ids(catalog_item_ids)
    return tuple(
        EquipmentUnit.objects.select_for_update()
        .filter(catalog_item_id__in=identifiers, status=UnitStatus.AVAILABLE)
        .order_by("pk")
    )
