"""Custom settings and audit views; live dashboard data belongs to T18."""

from typing import cast

from django.contrib import messages
from django.core.exceptions import ValidationError
from django.core.paginator import EmptyPage, Page, PageNotAnInteger, Paginator
from django.db.models import QuerySet
from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods, require_safe

from accounts.access import admin_required
from accounts.models import User
from operations.forms import AuditSearchForm, SettingsForm
from operations.models import AuditLog, SystemSetting
from operations.queries import audit_history, get_system_setting
from operations.services import update_settings


@require_safe
@admin_required
def dashboard(request: HttpRequest) -> HttpResponse:
    """Pending T18 destination; live dashboard data and charts belong to Alex."""
    return render(
        request,
        "operations/manage/pending.html",
        {
            "heading": "Administrator dashboard",
            "module": "T18 · Alex",
            "description": "Live cards for available units, pending requests, active loans, and overdue loans; a monthly issued-loan chart and an equipment-category usage chart will appear here.",
            "next_work": "Implement ORM-backed live cards and charts after T15 and T17 are integrated. All values must update when database transactions change; no static demonstration data.",
        },
    )


@require_safe
@admin_required
def profile(request: HttpRequest) -> HttpResponse:
    """Show only the signed-in administrator's current account and profile."""
    user: User = cast(User, request.user)
    return render(request, "operations/manage/profile.html", {"profile": user.profile})


@require_http_methods(["GET", "HEAD", "POST"])
@admin_required
def settings(request: HttpRequest) -> HttpResponse:
    """Display current limits and commit valid edits through the audited service."""
    setting: SystemSetting = get_system_setting()
    form: SettingsForm = SettingsForm(
        data=request.POST if request.method == "POST" else None,
        initial={
            "max_loan_days": setting.max_loan_days,
            "max_quantity_per_item": setting.max_quantity_per_item,
        },
    )
    if request.method == "POST" and form.is_valid():
        try:
            update_settings(
                actor_id=cast(User, request.user).pk,
                max_loan_days=form.cleaned_data["max_loan_days"],
                max_quantity_per_item=form.cleaned_data["max_quantity_per_item"],
            )
        except ValidationError as error:
            form.add_error(None, error)
        else:
            messages.success(request, "Operational settings saved. New requests use these limits.")
            return redirect("operations:settings")
    return render(request, "operations/manage/settings.html", {"form": form, "setting": setting})


@require_safe
@admin_required
def audit_list(request: HttpRequest) -> HttpResponse:
    """Expose read-only audit search to active administrators with strict pagination."""
    form: AuditSearchForm = AuditSearchForm(request.GET)
    entries: QuerySet[AuditLog]
    if form.is_valid():
        entries = audit_history(
            search_query=form.cleaned_data["q"],
            action=form.cleaned_data["action"],
            actor_id=form.cleaned_data["actor"],
            date_from=form.cleaned_data["date_from"],
            date_to=form.cleaned_data["date_to"],
        )
    else:
        entries = AuditLog.objects.none()
    paginator: Paginator[AuditLog] = Paginator(entries, 25)
    try:
        page: Page[AuditLog] = paginator.page(request.GET.get("page", "1"))
    except (PageNotAnInteger, EmptyPage) as error:
        raise Http404("The requested audit history page does not exist.") from error
    return render(request, "operations/manage/audit_list.html", {"form": form, "page": page})
