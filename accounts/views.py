"""Shared authentication views and the initial protected portal landing page."""

from typing import cast
from urllib.parse import urlsplit

from django.contrib.auth import login, logout
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.urls import Resolver404, resolve, reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_http_methods, require_POST, require_safe

from accounts.access import active_login_required, basic_user_required, require_active_user
from accounts.forms import LoginForm
from accounts.models import User, UserRole

ADMIN_NEXT_NAMESPACES: frozenset[str] = frozenset(
    {"accounts", "borrowing_manage", "inventory_manage", "operations"}
)


def _role_home_name(user: User) -> str:
    active_user: User = require_active_user(user)
    if active_user.role == UserRole.ADMIN:
        return "operations:dashboard"
    if active_user.role == UserRole.BASIC_USER:
        return "portal:home"
    raise PermissionDenied("Authenticated account has no supported product role.")


def _safe_role_next_url(request: HttpRequest, user: User) -> str | None:
    candidate: str = request.POST.get("next", "") or request.GET.get("next", "")
    if not candidate or not url_has_allowed_host_and_scheme(
        candidate,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        return None
    path: str = urlsplit(candidate).path
    try:
        namespace: str = resolve(path).namespace
    except Resolver404:
        return None
    if (
        user.role == UserRole.ADMIN
        and path.startswith("/manage/")
        and namespace in ADMIN_NEXT_NAMESPACES
    ):
        return candidate
    if user.role == UserRole.BASIC_USER and path.startswith("/portal/") and namespace == "portal":
        return candidate
    return None


@require_safe
def home(request: HttpRequest) -> HttpResponse:
    """Send anonymous visitors to login and active users to their role home."""
    if not request.user.is_authenticated:
        return redirect(f"{reverse('accounts:login')}?next={reverse('accounts:home')}")
    user: User = require_active_user(cast(User, request.user))
    return redirect(_role_home_name(user))


@require_http_methods(["GET", "POST"])
def login_view(request: HttpRequest) -> HttpResponse:
    """Authenticate through Django and redirect only to a role-appropriate path."""
    if request.user.is_authenticated:
        user: User = require_active_user(cast(User, request.user))
        return redirect(_role_home_name(user))
    form: LoginForm = LoginForm(
        request=request, data=request.POST if request.method == "POST" else None
    )
    if request.method == "POST" and form.is_valid():
        authenticated_user: User = cast(User, form.get_user())
        login(request, authenticated_user)
        next_url: str | None = _safe_role_next_url(request, authenticated_user)
        return redirect(next_url or reverse(_role_home_name(authenticated_user)))
    return render(
        request,
        "accounts/login.html",
        {"form": form, "next": request.POST.get("next", request.GET.get("next", ""))},
    )


@require_POST
@active_login_required
def logout_view(request: HttpRequest) -> HttpResponse:
    """End the current session through a CSRF-protected POST."""
    logout(request)
    return redirect("accounts:login")


@require_safe
@basic_user_required
def portal_home(request: HttpRequest) -> HttpResponse:
    """Provide the protected role destination until portal features are integrated."""
    return render(request, "accounts/portal/home.html")
