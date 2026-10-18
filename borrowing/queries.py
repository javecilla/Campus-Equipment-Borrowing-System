"""Read-only searches for the administrator request queue."""

from datetime import date

from django.db.models import Count, Q, QuerySet

from borrowing.models import BorrowRequest


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