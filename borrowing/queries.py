"""Read-only queries: administrator request queue/detail and owner-scoped borrower history."""

from dataclasses import dataclass
from datetime import date

from django.db.models import (
    BooleanField,
    Case,
    Count,
    F,
    Func,
    IntegerField,
    Prefetch,
    Q,
    QuerySet,
    Value,
    When,
)
from django.utils import timezone

from borrowing.models import (
    BorrowRequest,
    Loan,
    LoanUnit,
    RequestItem,
    RequestStatus,
    UnitAllocation,
)
from inventory.models import EquipmentUnit, UnitStatus


def with_loan_progress(loans: QuerySet[Loan], today: date) -> QuerySet[Loan]:
    """Derive progress and calendar-day overdue values without persisting a status.

    Each loan unit has at most one return, so these counts share one nonmultiplying
    join. Call before introducing other to-many joins in reporting queries.
    """
    return loans.annotate(
        issued_quantity=Count("units"),
        returned_quantity=Count("units__return_record"),
        outstanding_quantity=Count("units", filter=Q(units__return_record__isnull=True)),
    ).annotate(
        is_active=Case(
            When(outstanding_quantity__gt=0, then=Value(True)),
            default=Value(False),
            output_field=BooleanField(),
        ),
        is_overdue=Case(
            When(outstanding_quantity__gt=0, due_date__lt=today, then=Value(True)),
            default=Value(False),
            output_field=BooleanField(),
        ),
        overdue_days=Case(
            When(
                outstanding_quantity__gt=0,
                due_date__lt=today,
                then=Func(
                    Value(today),
                    F("due_date"),
                    arg_joiner=" - ",
                    template="(%(expressions)s)",
                    output_field=IntegerField(),
                ),
            ),
            default=Value(0),
            output_field=IntegerField(),
        ),
    )


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
        if search_query.isdecimal() and len(search_query) <= 18:
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
        UnitAllocation.objects.filter(
            request_item__request=borrow_request,
            ended_at__isnull=True,
            released_at__isnull=True,
        )
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


@dataclass(frozen=True)
class BorrowerWorkspace:
    pending_requests: int
    approved_requests: int
    active_loans: int
    overdue_loans: int
    recent_requests: tuple[BorrowRequest, ...]
    due_loans: tuple[Loan, ...]


def borrower_workspace(owner_id: int, today: date) -> BorrowerWorkspace:
    """Summarize only this owner's history; bounded previews keep the home page small.

    Reuse return-aware loan progress so partial returns remain active, final returns
    disappear from the due list, and a loan due today is not marked overdue.
    """
    requests = BorrowRequest.objects.filter(owner_id=owner_id)
    request_counts = requests.aggregate(
        pending=Count("pk", filter=Q(status=RequestStatus.PENDING)),
        approved=Count("pk", filter=Q(status=RequestStatus.APPROVED)),
    )
    loans = with_loan_progress(Loan.objects.filter(request__owner_id=owner_id), today)
    loan_counts = loans.aggregate(
        active=Count("pk", filter=Q(is_active=True)),
        overdue=Count("pk", filter=Q(is_overdue=True)),
    )
    return BorrowerWorkspace(
        pending_requests=request_counts["pending"],
        approved_requests=request_counts["approved"],
        active_loans=loan_counts["active"],
        overdue_loans=loan_counts["overdue"],
        recent_requests=tuple(request_history(owner_id, "")[:5]),
        due_loans=tuple(
            loans.filter(is_active=True).select_related("request").order_by("due_date", "pk")[:5]
        ),
    )


def loan_history(owner_id: int) -> QuerySet[Loan]:
    """Return only the owner's loans with issued units and return records loaded."""
    loan_units: QuerySet[LoanUnit] = (
        LoanUnit.objects.select_related("allocation__unit__catalog_item")
        .prefetch_related("return_record")
        .order_by("pk")
    )
    return (
        with_loan_progress(Loan.objects.filter(request__owner_id=owner_id), timezone.localdate())
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
        with_loan_progress(
            Loan.objects.filter(request__owner_id=owner_id, request_id=request_id),
            timezone.localdate(),
        )
        .prefetch_related(Prefetch("units", queryset=loan_units))
        .first()
    )


def manage_loan_history(search_query: str) -> QuerySet[Loan]:
    """List issued loans with counts that do not multiply across return joins."""
    loans: QuerySet[Loan] = with_loan_progress(
        Loan.objects.select_related("request__owner", "issued_by"), timezone.localdate()
    ).order_by("-issued_at", "-pk")
    if search_query:
        condition: Q = Q(request__owner__username__icontains=search_query)
        if search_query.isdecimal() and len(search_query) <= 18:
            condition |= Q(pk=int(search_query))
        loans = loans.filter(condition)
    return loans


def manage_loan_details() -> QuerySet[Loan]:
    """Load the same authoritative loan and asset relationships for detail and print views."""
    return manage_loan_history("").prefetch_related(
        Prefetch(
            "units",
            queryset=LoanUnit.objects.select_related(
                "allocation__unit__catalog_item", "return_record"
            ).order_by("allocation__unit__asset_code", "pk"),
        )
    )
