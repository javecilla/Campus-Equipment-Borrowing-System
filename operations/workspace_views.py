"""Read-only UI placeholders; workflow implementation remains with the named task owners."""

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_safe

from accounts.access import admin_required


@require_safe
@admin_required
def settings(request: HttpRequest) -> HttpResponse:
    """Display the pending T06 · Jerome module without reading or changing domain records."""
    return render(
        request,
        "operations/manage/pending.html",
        {
            "heading": "Operational settings",
            "module": "T06 · Jerome",
            "description": "Loan duration and quantity limits will be configured here.",
            "next_work": "Add the custom validated settings form using the existing audited settings service. New limits apply to newly submitted requests.",
        },
    )


@require_safe
@admin_required
def audit_list(request: HttpRequest) -> HttpResponse:
    """Display the pending T06 · Jerome module without reading or changing domain records."""
    return render(
        request,
        "operations/manage/pending.html",
        {
            "heading": "Audit history",
            "module": "T06 · Jerome",
            "description": "Searchable administrator-only records of operational changes will appear here.",
            "next_work": "Add reference, action, actor, and date filters with pagination. Keep audit records read-only and restricted to administrators.",
        },
    )


@require_safe
@admin_required
def loan_report(request: HttpRequest) -> HttpResponse:
    """Display the pending T19 · Alex module without reading or changing domain records."""
    return render(
        request,
        "operations/manage/pending.html",
        {
            "heading": "Reports",
            "module": "T19 · Alex",
            "description": "Loan summaries, overdue reports, and CSV exports will appear here.",
            "next_work": "Build reports from live loan and return records after T17 and T18. Verify filtered totals and spreadsheet-safe exports.",
        },
    )
