"""Read-only queries for custom basic-user account management."""

from django.db.models import Q, QuerySet

from accounts.models import User, UserRole
from borrowing.models import BorrowRequest, Loan


def basic_user_accounts(search_query: str, active: bool | None) -> QuerySet[User]:
    """Return BASIC_USER rows matching the documented search and status filters."""
    accounts: QuerySet[User] = User.objects.filter(role=UserRole.BASIC_USER).select_related(
        "profile"
    )
    if search_query:
        accounts = accounts.filter(
            Q(username__icontains=search_query)
            | Q(first_name__icontains=search_query)
            | Q(last_name__icontains=search_query)
            | Q(email__icontains=search_query)
            | Q(profile__contact_number__icontains=search_query)
        )
    if active is not None:
        accounts = accounts.filter(is_active=active)
    return accounts.order_by("username", "pk")


def basic_user_account(account_id: int) -> User:
    """Resolve one BASIC_USER with its required profile or raise DoesNotExist."""
    return User.objects.select_related("profile").get(pk=account_id, role=UserRole.BASIC_USER)


def account_request_history(account_id: int) -> QuerySet[BorrowRequest]:
    """Return the target user's immutable request history for display."""
    return (
        BorrowRequest.objects.filter(owner_id=account_id)
        .select_related("decided_by", "cancelled_by")
        .prefetch_related("items__catalog_item")
        .order_by("-submitted_at", "-pk")
    )


def account_loan_history(account_id: int) -> QuerySet[Loan]:
    """Return loans reached through requests owned by the target user."""
    return (
        Loan.objects.filter(request__owner_id=account_id)
        .select_related("request", "issued_by")
        .prefetch_related("units__allocation__unit")
        .order_by("-issued_at", "-pk")
    )
