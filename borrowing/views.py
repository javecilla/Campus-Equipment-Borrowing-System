"""Borrower request submission and the administrator request queue, detail and decisions."""

from datetime import date
from typing import cast

from django.contrib import messages
from django.core.exceptions import ValidationError
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.forms import BaseFormSet
from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_http_methods, require_safe

from accounts.access import admin_required, basic_user_required
from accounts.models import User
from borrowing.forms import DecisionForm, RequestForm, RequestItemFormSetFactory, RequestQueueForm
from borrowing.models import BorrowRequest
from borrowing.queries import request_lines, request_queue
from borrowing.services import WorkflowConflict, approve_request, reject_request, submit_request
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
    """Searchable, filterable queue of borrow requests, 25 per page."""
    form = RequestQueueForm(request.GET)
    if form.is_valid():
        queue = request_queue(
            search_query=form.cleaned_data["q"],
            status=form.cleaned_data["status"],
            date_from=form.cleaned_data["date_from"],
            date_to=form.cleaned_data["date_to"],
        )
    else:
        queue = BorrowRequest.objects.none()
    paginator = Paginator(queue, 25)
    try:
        page = paginator.page(request.GET.get("page", "1"))
    except (PageNotAnInteger, EmptyPage) as error:
        raise Http404("The requested queue page does not exist.") from error
    return render(request, "borrowing/manage/request_list.html", {"form": form, "page": page})


@require_safe
@admin_required
def request_detail(request: HttpRequest, request_id: int) -> HttpResponse:
    """Read-only review of one request: items, current availability, and decision history."""
    borrow_request = get_object_or_404(
        BorrowRequest.objects.select_related("owner", "decided_by", "cancelled_by"), pk=request_id
    )
    return render(
        request,
        "borrowing/manage/request_detail.html",
        {"borrow_request": borrow_request, "lines": request_lines(borrow_request)},
    )


def _decide(
    request: HttpRequest, request_id: int, service, heading: str, button: str
) -> HttpResponse:
    """GET shows a confirmation form and changes nothing; POST applies the decision."""
    borrow_request = get_object_or_404(BorrowRequest.objects.select_related("owner"), pk=request_id)
    form = DecisionForm(request.POST if request.method == "POST" else None)
    conflict = None
    status = 200
    if request.method == "POST" and form.is_valid():
        try:
            service(cast(User, request.user).pk, borrow_request.pk, form.cleaned_data["reason"])
        except WorkflowConflict as error:
            conflict, status = str(error), 409
        except ValidationError as error:
            form.add_error(None, error)
        else:
            return redirect("borrowing_manage:request-detail", request_id=borrow_request.pk)
    context = {
        "borrow_request": borrow_request,
        "form": form,
        "conflict": conflict,
        "heading": heading,
        "button": button,
    }
    return render(request, "borrowing/manage/request_decision.html", context, status=status)


@require_http_methods(["GET", "HEAD", "POST"])
@admin_required
def request_approve(request: HttpRequest, request_id: int) -> HttpResponse:
    return _decide(
        request, request_id, approve_request, "Approve request", "Approve and reserve units"
    )


@require_http_methods(["GET", "HEAD", "POST"])
@admin_required
def request_reject(request: HttpRequest, request_id: int) -> HttpResponse:
    return _decide(request, request_id, reject_request, "Reject request", "Reject request")


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
