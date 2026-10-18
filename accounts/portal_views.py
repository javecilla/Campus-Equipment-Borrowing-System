"""Borrower profile and remaining portal placeholder views."""

from typing import cast

from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

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
