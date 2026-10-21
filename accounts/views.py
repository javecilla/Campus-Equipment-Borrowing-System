"""Authentication, portal landing, and custom account-management views."""

from typing import cast
from urllib.parse import urlsplit

from django.contrib import messages
from django.contrib.auth import login, logout
from django.core.exceptions import PermissionDenied
from django.core.paginator import EmptyPage, Page, PageNotAnInteger, Paginator
from django.db.models import QuerySet
from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.urls import Resolver404, resolve, reverse
from django.utils import timezone
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_http_methods, require_POST, require_safe

from accounts.access import (
    active_login_required,
    admin_required,
    basic_user_required,
    require_active_user,
)
from accounts.forms import AccountSearchForm, AccountStatusForm, LoginForm, RegistrationForm
from accounts.models import User, UserRole
from accounts.queries import (
    account_loan_history,
    account_request_history,
    basic_user_account,
    basic_user_accounts,
)
from accounts.services import (
    AccountStatusConflict,
    activate_basic_user,
    deactivate_basic_user,
    register_basic_user,
)
from borrowing.models import BorrowRequest, Loan
from borrowing.queries import borrower_workspace

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


@require_http_methods(["GET", "POST"])
def register_view(request: HttpRequest) -> HttpResponse:
    """Register a new student account as an active BASIC_USER."""
    if request.user.is_authenticated:
        user: User = require_active_user(cast(User, request.user))
        return redirect(_role_home_name(user))
    form: RegistrationForm = RegistrationForm(
        data=request.POST if request.method == "POST" else None
    )
    if request.method == "POST" and form.is_valid():
        register_basic_user(
            username=form.cleaned_data["username"],
            first_name=form.cleaned_data["first_name"],
            last_name=form.cleaned_data["last_name"],
            email=form.cleaned_data["email"],
            contact_number=str(form.cleaned_data.get("contact_number") or ""),
            raw_password=form.cleaned_data["password1"],
        )
        messages.success(
            request,
            "Your account has been created successfully. You may now sign in.",
        )
        return redirect("accounts:login")
    return render(request, "accounts/register.html", {"form": form})


@require_safe
@basic_user_required
def portal_home(request: HttpRequest) -> HttpResponse:
    """Show the active borrower's own request and return-aware loan overview."""
    user: User = cast(User, request.user)
    return render(
        request,
        "accounts/portal/home.html",
        {"workspace": borrower_workspace(user.pk, timezone.localdate())},
    )


def _basic_user_or_404(account_id: int) -> User:
    try:
        return basic_user_account(account_id)
    except User.DoesNotExist as error:
        raise Http404("The requested basic-user account does not exist.") from error


@require_safe
@admin_required
def manage_account_list(request: HttpRequest) -> HttpResponse:
    """List and search BASIC_USER accounts with the required fixed pagination."""
    form = AccountSearchForm(request.GET)
    accounts: QuerySet[User]
    if form.is_valid():
        search_query: str = form.cleaned_data["q"]
        active: bool | None = form.cleaned_data["active"]
        accounts = basic_user_accounts(search_query, active)
    else:
        accounts = User.objects.none()
    paginator = Paginator(accounts, 25)
    try:
        page: Page[User] = paginator.page(request.GET.get("page", "1"))
    except (PageNotAnInteger, EmptyPage) as error:
        raise Http404("The requested account page does not exist.") from error
    return render(request, "accounts/manage/list.html", {"form": form, "page": page})


@require_safe
@admin_required
def manage_account_detail(request: HttpRequest, account_id: int) -> HttpResponse:
    """Show one basic user's profile plus preserved request and loan history."""
    account: User = _basic_user_or_404(account_id)
    request_history: QuerySet[BorrowRequest] = account_request_history(account.pk)
    loan_history: QuerySet[Loan] = account_loan_history(account.pk)
    return render(
        request,
        "accounts/manage/detail.html",
        {
            "account": account,
            "request_history": request_history,
            "loan_history": loan_history,
        },
    )


@require_http_methods(["GET", "POST"])
@admin_required
def manage_account_activate(request: HttpRequest, account_id: int) -> HttpResponse:
    """Confirm and perform the explicit BASIC_USER activation action."""
    account: User = _basic_user_or_404(account_id)
    form = AccountStatusForm(request.POST if request.method == "POST" else None)
    if request.method == "POST" and form.is_valid():
        try:
            activate_basic_user(cast(User, request.user).pk, account.pk)
        except AccountStatusConflict as error:
            return render(
                request,
                "accounts/manage/status_confirmation.html",
                {"account": account, "form": form, "action_label": "Activate", "error": error},
                status=409,
            )
        except User.DoesNotExist as error:
            raise Http404("The requested basic-user account does not exist.") from error
        messages.success(request, "The basic-user account was activated.")
        return redirect("accounts:manage-detail", account_id=account.pk)
    return render(
        request,
        "accounts/manage/status_confirmation.html",
        {"account": account, "form": form, "action_label": "Activate"},
    )


@require_http_methods(["GET", "POST"])
@admin_required
def manage_account_deactivate(request: HttpRequest, account_id: int) -> HttpResponse:
    """Confirm and perform deactivation without changing transaction history."""
    account: User = _basic_user_or_404(account_id)
    form = AccountStatusForm(request.POST if request.method == "POST" else None)
    if request.method == "POST" and form.is_valid():
        try:
            deactivate_basic_user(cast(User, request.user).pk, account.pk)
        except AccountStatusConflict as error:
            return render(
                request,
                "accounts/manage/status_confirmation.html",
                {
                    "account": account,
                    "form": form,
                    "action_label": "Deactivate",
                    "error": error,
                },
                status=409,
            )
        except User.DoesNotExist as error:
            raise Http404("The requested basic-user account does not exist.") from error
        messages.success(request, "The basic-user account was deactivated.")
        return redirect("accounts:manage-detail", account_id=account.pk)
    return render(
        request,
        "accounts/manage/status_confirmation.html",
        {"account": account, "form": form, "action_label": "Deactivate"},
    )
