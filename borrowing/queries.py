"""Owner-scoped, read-only borrower request and loan history queries."""

from django.db.models import Prefetch, QuerySet

from borrowing.models import BorrowRequest, Loan, LoanUnit, RequestItem


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
