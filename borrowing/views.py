"""Borrower request submission and read-only administration placeholders."""

from datetime import date
from typing import cast

from django.contrib import messages
from django.core.exceptions import ValidationError
from django.forms import BaseFormSet
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views.decorators.http import require_http_methods, require_safe

from accounts.access import admin_required, basic_user_required
from accounts.models import User
from borrowing.forms import RequestForm, RequestItemFormSetFactory
from borrowing.models import BorrowRequest
from borrowing.services import submit_request
from operations.queries import get_loan_limits
from operations.validation import LoanLimits, RequestedItem


@require_http_methods(["GET", "POST"])
@basic_user_required
def request_create(request: HttpRequest) -> HttpResponse:
    """Validate and submit a new Pending request for the signed-in borrower."""
    user: User = cast(User, request.user)
    limits: LoanLimits = get_loan_limits()
    submitted_on: date = timezone.localdate()
    is_bound: bool = request.method == "POST"
    form: RequestForm = RequestForm(
        request.POST if is_bound else None,
        limits=limits,
        submitted_on=submitted_on,
    )
    item_formset: BaseFormSet = RequestItemFormSetFactory(
        request.POST if is_bound else None,
        prefix="items",
        form_kwargs={"max_quantity": limits.max_quantity_per_item},
    )

    if is_bound and form.is_valid() and item_formset.is_valid():
        requested_items: tuple[RequestedItem, ...] = tuple(
            RequestedItem(
                catalog_item_id=item_form.cleaned_data["catalog_item"].pk,
                quantity=item_form.cleaned_data["quantity"],
            )
            for item_form in item_formset.forms
            if item_form.cleaned_data
        )
        try:
            borrow_request: BorrowRequest = submit_request(
                owner_id=user.pk,
                purpose=form.cleaned_data["purpose"],
                desired_due_date=form.cleaned_data["desired_due_date"],
                items=requested_items,
            )
        except ValidationError as error:
            form.add_error(None, error.messages)
        else:
            messages.success(
                request,
                f"Request #{borrow_request.pk} was submitted for administrator review.",
            )
            return redirect("portal:request-list")

    return render(
        request,
        "borrowing/portal/request_form.html",
        {
            "form": form,
            "item_formset": item_formset,
            "limits": limits,
        },
    )


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
