"""Read-only UI placeholders; workflow implementation remains with the named task owners."""

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_safe

from accounts.access import admin_required


@require_safe
@admin_required
def request_list(request: HttpRequest) -> HttpResponse:
    """Display the pending T13 / T15 / T17 · Margareth module without reading or changing domain records."""
    return render(
        request,
        "operations/manage/pending.html",
        {
            "heading": "Requests and approvals",
            "module": "T13 / T15 / T17 · Margareth",
            "description": "Review requests, approve or reject them, and follow their release and return progress.",
            "next_work": "Add the request queue after T11. Release requires the T14 concurrency proof; returns also require T16 maintenance.",
        },
    )


@require_safe
@admin_required
def loan_list(request: HttpRequest) -> HttpResponse:
    """Display the pending T15 / T17 · Margareth with Kenneth module without reading or changing domain records."""
    return render(
        request,
        "operations/manage/pending.html",
        {
            "heading": "Releases and returns",
            "module": "T15 / T17 · Margareth with Kenneth",
            "description": "Issued equipment, borrowing slips, due dates, and per-unit returns will appear here.",
            "next_work": "Implement audited one-time release and partial or damaged returns after their prerequisite workflows are integrated.",
        },
    )
