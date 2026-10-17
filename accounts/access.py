"""Reusable active-account, role, and portal-ownership enforcement."""

from collections.abc import Callable
from functools import wraps
from typing import Concatenate, Literal, ParamSpec, TypeVar, cast

from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import PermissionDenied
from django.db.models import Model, QuerySet
from django.http import Http404, HttpRequest
from django.http.response import HttpResponseBase
from django.shortcuts import get_object_or_404
from django.urls import reverse

from accounts.models import User, UserRole

ViewParameters = ParamSpec("ViewParameters")
ViewResponse = TypeVar("ViewResponse", bound=HttpResponseBase)
OwnedModel = TypeVar("OwnedModel", bound=Model)
OwnershipLookup = Literal["owner_id", "request__owner_id"]
OWNERSHIP_LOOKUPS: frozenset[str] = frozenset({"owner_id", "request__owner_id"})


def require_active_user(user: User) -> User:
    """Return an active authenticated user or deny the operation."""
    if not user.is_authenticated or not user.is_active:
        raise PermissionDenied("An active account is required.")
    return user


def require_active_admin(user: User) -> User:
    """Return an active ADMIN without trusting Django staff/superuser flags."""
    active_user: User = require_active_user(user)
    if active_user.role != UserRole.ADMIN:
        raise PermissionDenied("Administrator access is required.")
    return active_user


def require_active_basic_user(user: User) -> User:
    """Return an active BASIC_USER without trusting submitted role data."""
    active_user: User = require_active_user(user)
    if active_user.role != UserRole.BASIC_USER:
        raise PermissionDenied("Basic-user access is required.")
    return active_user


def active_login_required(
    view_function: Callable[Concatenate[HttpRequest, ViewParameters], ViewResponse],
) -> Callable[Concatenate[HttpRequest, ViewParameters], HttpResponseBase]:
    """Redirect anonymous requests and deny authenticated inactive accounts."""

    @wraps(view_function)
    def wrapped_view(
        request: HttpRequest,
        *args: ViewParameters.args,
        **kwargs: ViewParameters.kwargs,
    ) -> HttpResponseBase:
        if not request.user.is_authenticated:
            return redirect_to_login(request.get_full_path(), reverse("accounts:login"))
        user: User = require_active_user(cast(User, request.user))
        request.user = user
        return view_function(request, *args, **kwargs)

    return wrapped_view


def _role_required(
    required_role: UserRole,
    view_function: Callable[Concatenate[HttpRequest, ViewParameters], ViewResponse],
) -> Callable[Concatenate[HttpRequest, ViewParameters], HttpResponseBase]:
    @active_login_required
    @wraps(view_function)
    def wrapped_view(
        request: HttpRequest,
        *args: ViewParameters.args,
        **kwargs: ViewParameters.kwargs,
    ) -> HttpResponseBase:
        user: User = cast(User, request.user)
        if required_role == UserRole.ADMIN:
            require_active_admin(user)
        else:
            require_active_basic_user(user)
        return view_function(request, *args, **kwargs)

    return wrapped_view


def admin_required(
    view_function: Callable[Concatenate[HttpRequest, ViewParameters], ViewResponse],
) -> Callable[Concatenate[HttpRequest, ViewParameters], HttpResponseBase]:
    """Require the stored ADMIN role for a custom management view."""
    return _role_required(UserRole.ADMIN, view_function)


def basic_user_required(
    view_function: Callable[Concatenate[HttpRequest, ViewParameters], ViewResponse],
) -> Callable[Concatenate[HttpRequest, ViewParameters], HttpResponseBase]:
    """Require the stored BASIC_USER role for a portal view."""
    return _role_required(UserRole.BASIC_USER, view_function)


def get_owned_object_or_404(
    queryset: QuerySet[OwnedModel],
    user: User,
    object_id: int,
    owner_lookup: OwnershipLookup,
) -> OwnedModel:
    """Resolve a portal record under its signed-in BASIC_USER owner scope."""
    owner: User = require_active_basic_user(user)
    if type(object_id) is not int or object_id < 1:
        raise Http404("The requested record does not exist.")
    if owner_lookup not in OWNERSHIP_LOOKUPS:
        raise ValueError("Ownership lookup must use an approved owner relationship.")
    return cast(
        OwnedModel,
        get_object_or_404(queryset, pk=object_id, **{owner_lookup: owner.pk}),
    )
