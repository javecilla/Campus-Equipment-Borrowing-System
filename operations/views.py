"""Protected custom-management landing view; live dashboard data belongs to T18."""

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_safe

from accounts.access import admin_required


@require_safe
@admin_required
def dashboard(request: HttpRequest) -> HttpResponse:
    """Provide the ADMIN role destination without static dashboard metrics."""
    return render(request, "operations/manage/dashboard.html")
