"""Read-only queries: administrator request queue/detail and owner-scoped borrower history."""

from datetime import date

from django.db.models import Count, Prefetch, Q, QuerySet

from borrowing.models import BorrowRequest, Loan, LoanUnit, RequestItem, UnitAllocation
from inventory.models import EquipmentUnit, UnitStatus


def request_queue(
    search_query: str = "",
    status: str = "",
    date_from: date | None = None,
    date_to: date | None = None,
) -> QuerySet[BorrowRequest]:
    """Newest submissions first; the search matches a request ID or borrower username."""
    requests = (
        BorrowRequest.objects.select_related("owner")
        .annotate(item_count=Count("items"))
        .order_by("-submitted_at", "-pk")
    )
    if search_query:
        condition = Q(owner__username__icontains=search_query)
        if search_query.isdigit() and len(search_query) <= 18:
            condition |= Q(pk=int(search_query))
        requests = requests.filter(condition)
    if status:
        requests = requests.filter(status=status)
    if date_from is not None:
        requests = requests.filter(submitted_on__gte=date_from)
    if date_to is not None:
        requests = requests.filter(submitted_on__lte=date_to)
    return requests


def request_lines(borrow_request: BorrowRequest) -> list[dict]:
    """Each requested item with its current availability and any reserved units."""
    items = list(borrow_request.items.select_related("catalog_item__category").order_by("pk"))
    available = dict(
        EquipmentUnit.objects.filter(
            catalog_item_id__in=[item.catalog_item_id for item in items],
            status=UnitStatus.AVAILABLE,
        )
        .order_by()
        .values_list("catalog_item_id")
        .annotate(total=Count("pk"))
    )
    allocations = (
        UnitAllocation.objects.filter(request_item__request=borrow_request)
        .select_related("unit")
        .order_by("unit__asset_code")
    )
    units_by_line: dict[int, list[UnitAllocation]] = {}
    for allocation in allocations:
        units_by_line.setdefault(allocation.request_item_id, []).append(allocation)
    return [
        {
            "line": item,
            "available": available.get(item.catalog_item_id, 0),
            "units": units_by_line.get(item.pk, []),
        }
        for item in items
    ]


def request_history(owner_id: int, status: str) -> QuerySet[BorrowRequest]:
    """Return only the owner's requests, with their items ready for list rendering."""
    requests: QuerySet[BorrowRequest] = (
        BorrowRequest.objects.filter(owner_id=owner_id)
        .prefetch_related(
            Prefetch(
                "items",
                queryset=RequestItem.objects.select_related(
                    "catalog_item", "catalog_item__category"
                ).order_by("pk"),
            )
        )
        .order_by("-submitted_at", "-pk")
    )
    if status:
        requests = requests.filter(status=status)
    return requests


def loan_history(owner_id: int) -> QuerySet[Loan]:
    """Return only the owner's loans with issued units and return records loaded."""
    loan_units: QuerySet[LoanUnit] = (
        LoanUnit.objects.select_related("allocation__unit__catalog_item")
        .prefetch_related("return_record")
        .order_by("pk")
    )
    return (
        Loan.objects.filter(request__owner_id=owner_id)
        .select_related("request")
        .prefetch_related(Prefetch("units", queryset=loan_units))
        .order_by("-issued_at", "-pk")
    )


def loan_for_request(owner_id: int, request_id: int) -> Loan | None:
    """Return the owner's loan for one request, if the request has been issued."""
    loan_units: QuerySet[LoanUnit] = (
        LoanUnit.objects.select_related("allocation__unit__catalog_item")
        .prefetch_related("return_record")
        .order_by("pk")
    )
    return (
        Loan.objects.filter(request__owner_id=owner_id, request_id=request_id)
        .prefetch_related(Prefetch("units", queryset=loan_units))
        .first()
    )
