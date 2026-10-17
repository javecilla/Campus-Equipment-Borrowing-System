"""Read-only UI placeholders; workflow implementation remains with the named task owners."""

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_safe

from accounts.access import admin_required


@require_safe
@admin_required
def item_list(request: HttpRequest) -> HttpResponse:
    """Display the pending T07 · Kenneth module without reading or changing domain records."""
    return render(
        request,
        "operations/manage/pending.html",
        {
            "heading": "Equipment catalog",
            "module": "T07 · Kenneth",
            "description": "Categories and equipment descriptions will be managed here.",
            "next_work": "Add validated catalog search, pagination, create/update, and archive actions after reviewing the T07 contract.",
        },
    )


@require_safe
@admin_required
def unit_list(request: HttpRequest) -> HttpResponse:
    """Display the pending T08 · Kenneth module without reading or changing domain records."""
    return render(
        request,
        "operations/manage/pending.html",
        {
            "heading": "Physical units",
            "module": "T08 · Kenneth",
            "description": "Individual campus assets and their availability will appear here.",
            "next_work": "Add asset registration, filters, derived counts, and protected unit history after T07 is integrated.",
        },
    )


@require_safe
@admin_required
def maintenance_list(request: HttpRequest) -> HttpResponse:
    """Display the pending T16 · Kenneth module without reading or changing domain records."""
    return render(
        request,
        "operations/manage/pending.html",
        {
            "heading": "Maintenance",
            "module": "T16 · Kenneth",
            "description": "Equipment repairs, maintenance history, and retirement will be managed here.",
            "next_work": "Add audited maintenance opening and closure after T08. Reserved and issued units must remain protected.",
        },
    )
