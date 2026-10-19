"""Read-only queries for categories, catalog items, and inventory counts."""

from dataclasses import dataclass

from django.db.models import Count, Q, QuerySet
from django.http import Http404

from borrowing.models import RequestItem, UnitAllocation
from inventory.models import (
    CatalogItem,
    Category,
    EquipmentUnit,
    MaintenanceRecord,
    MaintenanceStatus,
    UnitStatus,
)


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


def has_unit_transactional_history(unit_id: int) -> bool:
    """Return True if any allocations or maintenance records reference this physical unit."""
    return (
        UnitAllocation.objects.filter(unit_id=unit_id).exists()
        or MaintenanceRecord.objects.filter(unit_id=unit_id).exists()
    )


def get_overall_inventory_counts() -> ItemInventoryCounts:
    """Derive system-wide physical unit counts across all equipment."""
    result: dict[str, int | None] = EquipmentUnit.objects.aggregate(
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


def list_equipment_units(
    search_query: str,
    category_id: int | None,
    item_id: int | None,
    status: str | None,
) -> QuerySet[EquipmentUnit]:
    """Return physical units matching search, category, item, and status filters."""
    units: QuerySet[EquipmentUnit] = EquipmentUnit.objects.select_related(
        "catalog_item", "catalog_item__category"
    )
    if search_query:
        units = units.filter(
            Q(asset_code__icontains=search_query)
            | Q(internal_notes__icontains=search_query)
            | Q(catalog_item__name__icontains=search_query)
        )
    if category_id is not None:
        units = units.filter(catalog_item__category_id=category_id)
    if item_id is not None:
        units = units.filter(catalog_item_id=item_id)
    if status and status in UnitStatus.values:
        units = units.filter(status=status)
    return units.order_by("asset_code", "pk")


def get_unit_or_404(unit_id: int) -> EquipmentUnit:
    """Resolve an EquipmentUnit with related item and category, or raise Http404."""
    try:
        return EquipmentUnit.objects.select_related("catalog_item", "catalog_item__category").get(
            pk=unit_id
        )
    except EquipmentUnit.DoesNotExist as error:
        raise Http404("The requested physical unit does not exist.") from error


def get_unit_allocations(unit_id: int) -> QuerySet[UnitAllocation]:
    """Return allocations and associated loan/return details for this unit."""
    return (
        UnitAllocation.objects.filter(unit_id=unit_id)
        .select_related(
            "request_item__request__owner",
            "request_item__catalog_item",
            "allocated_by",
            "loan_unit__loan__issued_by",
            "loan_unit__return_record__received_by",
        )
        .order_by("-allocated_at", "-pk")
    )


def get_unit_maintenance_records(unit_id: int) -> QuerySet[MaintenanceRecord]:
    """Return maintenance history for this unit."""
    return (
        MaintenanceRecord.objects.filter(unit_id=unit_id)
        .select_related("opened_by", "closed_by", "source_return__received_by")
        .order_by("-opened_at", "-pk")
    )


def list_active_catalog_items(
    search_query: str,
    category_id: int | None,
) -> QuerySet[CatalogItem]:
    """Return active catalog items under active categories with serviceable and available counts."""
    items: QuerySet[CatalogItem] = (
        CatalogItem.objects.filter(
            is_archived=False,
            category__is_archived=False,
        )
        .select_related("category")
        .annotate(
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
    )
    if search_query:
        query_text: str = search_query.strip()
        items = items.filter(Q(name__icontains=query_text) | Q(description__icontains=query_text))
    if category_id is not None:
        items = items.filter(category_id=category_id)
    return items.order_by("name", "pk")


def get_active_catalog_item_or_404(item_id: int) -> CatalogItem:
    """Resolve an active CatalogItem under an active Category with counts, or raise Http404."""
    try:
        return (
            CatalogItem.objects.filter(
                is_archived=False,
                category__is_archived=False,
            )
            .select_related("category")
            .annotate(
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
            .get(pk=item_id)
        )
    except CatalogItem.DoesNotExist as error:
        raise Http404("The requested equipment item is not available.") from error


def list_maintenance_records(
    search_query: str,
    status: str | None,
) -> QuerySet[MaintenanceRecord]:
    """Return maintenance records matching optional search query and status filter."""
    records: QuerySet[MaintenanceRecord] = MaintenanceRecord.objects.select_related(
        "unit",
        "unit__catalog_item",
        "unit__catalog_item__category",
        "opened_by",
        "closed_by",
        "source_return__received_by",
    )
    if search_query:
        query_text: str = search_query.strip()
        records = records.filter(
            Q(unit__asset_code__icontains=query_text)
            | Q(problem__icontains=query_text)
            | Q(action__icontains=query_text)
            | Q(unit__catalog_item__name__icontains=query_text)
        )
    if status and status in MaintenanceStatus.values:
        records = records.filter(status=status)
    return records.order_by("-opened_at", "-pk")


def get_maintenance_or_404(maintenance_id: int) -> MaintenanceRecord:
    """Resolve a MaintenanceRecord with related unit, item, and actors, or raise Http404."""
    try:
        return MaintenanceRecord.objects.select_related(
            "unit",
            "unit__catalog_item",
            "unit__catalog_item__category",
            "opened_by",
            "closed_by",
            "source_return__received_by",
        ).get(pk=maintenance_id)
    except MaintenanceRecord.DoesNotExist as error:
        raise Http404("The requested maintenance record does not exist.") from error
