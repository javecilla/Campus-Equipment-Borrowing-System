"""Borrower-only UI placeholders for the assigned portal feature owners."""

from typing import cast

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_safe

from accounts.access import basic_user_required
from accounts.models import User


@require_safe
@basic_user_required
def profile(request: HttpRequest) -> HttpResponse:
    """Show the signed-in borrower's own profile; editing remains T09 scope."""
    user: User = cast(User, request.user)
    return render(request, "accounts/portal/profile.html", {"profile": user.profile})


@require_safe
@basic_user_required
def equipment_list(request: HttpRequest) -> HttpResponse:
    """Display the pending T10 · Ellyssa module without exposing another user's data."""
    return render(
        request,
        "accounts/portal/pending.html",
        {
            "heading": "Browse equipment",
            "module": "T10 · Ellyssa",
            "description": "Find campus equipment and check borrowing availability here.",
            "next_work": "Add active catalog search and item details after T08 and T09. Show only borrower-safe descriptions and quantities.",
        },
    )


@require_safe
@basic_user_required
def request_list(request: HttpRequest) -> HttpResponse:
    """Display the pending T11 / T12 · Ralph module without exposing another user's data."""
    return render(
        request,
        "accounts/portal/pending.html",
        {
            "heading": "My requests",
            "module": "T11 / T12 · Ralph",
            "description": "Submit borrowing requests and follow their progress here.",
            "next_work": "Add atomic request submission, your own request history, and eligible cancellation after T08 and T09. Enforce ownership on every lookup.",
        },
    )


@require_safe
@basic_user_required
def loan_list(request: HttpRequest) -> HttpResponse:
    """Display the pending T12 · Ralph module without exposing another user's data."""
    return render(
        request,
        "accounts/portal/pending.html",
        {
            "heading": "My loans",
            "module": "T12 · Ralph",
            "description": "Your issued equipment, due dates, and return progress will appear here.",
            "next_work": "Add owner-scoped loan lists and details after T11. Verify tracking against the integrated release and return workflows.",
        },
    )
