"""Read-only queries for categories, catalog items, and inventory counts."""

from dataclasses import dataclass

from django.db.models import Count, Q, QuerySet
from django.http import Http404

from borrowing.models import RequestItem
from inventory.models import CatalogItem, Category, EquipmentUnit, UnitStatus


@dataclass(frozen=True)
class ItemInventoryCounts:
    available: int
    reserved: int
    issued: int
    maintenance: int
    retired: int
    serviceable: int
    total: int


def has_transactional_history(item_id: int) -> bool:
    """Return True if any physical units or request items reference this catalog item."""
    return (
        EquipmentUnit.objects.filter(catalog_item_id=item_id).exists()
        or RequestItem.objects.filter(catalog_item_id=item_id).exists()
    )


def get_item_inventory_counts(catalog_item_id: int) -> ItemInventoryCounts:
    """Derive exact inventory totals and serviceable count via SQL aggregates per BR-12."""
    result: dict[str, int | None] = EquipmentUnit.objects.filter(
        catalog_item_id=catalog_item_id
    ).aggregate(
        available=Count("pk", filter=Q(status=UnitStatus.AVAILABLE)),
        reserved=Count("pk", filter=Q(status=UnitStatus.RESERVED)),
        issued=Count("pk", filter=Q(status=UnitStatus.ISSUED)),
        maintenance=Count("pk", filter=Q(status=UnitStatus.MAINTENANCE)),
        retired=Count("pk", filter=Q(status=UnitStatus.RETIRED)),
    )
    available: int = result["available"] or 0
    reserved: int = result["reserved"] or 0
    issued: int = result["issued"] or 0
    maintenance: int = result["maintenance"] or 0
    retired: int = result["retired"] or 0
    serviceable: int = available + reserved + issued
    total: int = available + reserved + issued + maintenance + retired
    return ItemInventoryCounts(
        available=available,
        reserved=reserved,
        issued=issued,
        maintenance=maintenance,
        retired=retired,
        serviceable=serviceable,
        total=total,
    )


def list_categories(search_query: str, archived: str | None) -> QuerySet[Category]:
    """Return categories matching search and archived filter with annotated item counts."""
    categories: QuerySet[Category] = Category.objects.annotate(item_count=Count("items"))
    if search_query:
        categories = categories.filter(
            Q(name__icontains=search_query) | Q(description__icontains=search_query)
        )
    if archived == "true":
        categories = categories.filter(is_archived=True)
    elif archived == "false":
        categories = categories.filter(is_archived=False)
    return categories.order_by("name", "pk")


def get_category_or_404(category_id: int) -> Category:
    """Resolve a Category with annotated item count or raise Http404."""
    try:
        return Category.objects.annotate(item_count=Count("items")).get(pk=category_id)
    except Category.DoesNotExist as error:
        raise Http404("The requested category does not exist.") from error


def category_items(category_id: int) -> QuerySet[CatalogItem]:
    """Return catalog items under the given category with annotated unit totals."""
    return (
        CatalogItem.objects.filter(category_id=category_id)
        .annotate(
            total_units=Count("units"),
            serviceable_units=Count(
                "units",
                filter=Q(
                    units__status__in=[
                        UnitStatus.AVAILABLE,
                        UnitStatus.RESERVED,
                        UnitStatus.ISSUED,
                    ]
                ),
            ),
        )
        .order_by("name", "pk")
    )


def list_catalog_items(
    search_query: str,
    category_id: int | None,
    archived: str | None,
) -> QuerySet[CatalogItem]:
    """Return catalog items matching search, category, and archived filters with annotated counts."""
    items: QuerySet[CatalogItem] = CatalogItem.objects.select_related("category").annotate(
        total_units=Count("units"),
        serviceable_units=Count(
            "units",
            filter=Q(
                units__status__in=[
                    UnitStatus.AVAILABLE,
                    UnitStatus.RESERVED,
                    UnitStatus.ISSUED,
                ]
            ),
        ),
        available_units=Count(
            "units",
            filter=Q(units__status=UnitStatus.AVAILABLE),
        ),
    )
    if search_query:
        items = items.filter(
            Q(name__icontains=search_query) | Q(description__icontains=search_query)
        )
    if category_id is not None:
        items = items.filter(category_id=category_id)
    if archived == "true":
        items = items.filter(is_archived=True)
    elif archived == "false":
        items = items.filter(is_archived=False)
    return items.order_by("name", "pk")


def get_catalog_item_or_404(item_id: int) -> CatalogItem:
    """Resolve one CatalogItem with its Category or raise Http404."""
    try:
        return CatalogItem.objects.select_related("category").get(pk=item_id)
    except CatalogItem.DoesNotExist as error:
        raise Http404("The requested equipment item does not exist.") from error
