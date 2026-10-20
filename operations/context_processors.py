"""Template context processors for the administrator workspace."""

from typing import cast

from django.http import HttpRequest

from accounts.models import User, UserRole
from operations.queries import pending_request_count


def nav_badges(request: HttpRequest) -> dict[str, int]:
    """Inject sidebar badge counts for active admin sessions.

    Returns ``nav_pending_requests`` — the number of PENDING borrow requests.
    Only runs a database query when the request is made by an authenticated,
    active ADMIN; all other sessions receive an empty dict so there is no
    overhead for basic users or anonymous visitors.
    """
    if not request.user.is_authenticated:
        return {}
    user: User = cast(User, request.user)
    if not user.is_active or user.role != UserRole.ADMIN:
        return {}
    return {"nav_pending_requests": pending_request_count()}
