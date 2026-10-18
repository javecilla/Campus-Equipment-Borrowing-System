"""Borrower profile and remaining portal placeholder views."""

from typing import cast

from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods, require_safe

from accounts.access import basic_user_required
from accounts.forms import ProfileForm
from accounts.models import User
from accounts.services import update_basic_user_profile


@require_http_methods(["GET", "POST"])
@basic_user_required
def profile(request: HttpRequest) -> HttpResponse:
    """View and update the signed-in borrower's personal name and contact details."""
    user: User = cast(User, request.user)
    if request.method == "POST":
        form = ProfileForm(request.POST, user)
        if form.is_valid():
            update_basic_user_profile(
                user_id=user.pk,
                first_name=form.cleaned_data["first_name"],
                last_name=form.cleaned_data["last_name"],
                email=form.cleaned_data["email"],
                contact_number=str(form.cleaned_data.get("contact_number") or ""),
            )
            messages.success(request, "Your profile has been updated.")
            return redirect("portal:profile")
    else:
        form = ProfileForm(None, user)

    return render(
        request,
        "accounts/portal/profile.html",
        {"form": form, "profile": user.profile},
    )


@require_safe
@basic_user_required
def request_list(request: HttpRequest) -> HttpResponse:
    """Display submission confirmation while T12 history and tracking remain pending."""
    return render(
        request,
        "accounts/portal/request_list.html",
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
