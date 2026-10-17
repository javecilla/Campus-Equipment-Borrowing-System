"""Read-only UI placeholders; workflow implementation remains with the named task owners."""

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_safe

from accounts.access import admin_required


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
