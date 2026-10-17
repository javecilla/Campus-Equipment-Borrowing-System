"""Protected custom-management landing view; live dashboard data belongs to T18."""

from typing import cast

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_safe

from accounts.access import admin_required
from accounts.models import User


@require_safe
@admin_required
def dashboard(request: HttpRequest) -> HttpResponse:
    """Provide the ADMIN role destination without static dashboard metrics."""
    return render(request, "operations/manage/dashboard.html")


@require_safe
@admin_required
def profile(request: HttpRequest) -> HttpResponse:
    """Show only the signed-in administrator's current account and profile."""
    user: User = cast(User, request.user)
    return render(request, "operations/manage/profile.html", {"profile": user.profile})
