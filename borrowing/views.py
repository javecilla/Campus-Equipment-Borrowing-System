"""Borrower request submission/history/cancellation and the administrator request queue."""

from datetime import date
from typing import cast

from django.contrib import messages
from django.core.exceptions import ValidationError
from django.core.paginator import EmptyPage, Page, PageNotAnInteger, Paginator
from django.db.models import Prefetch, Q, QuerySet
from django.forms import BaseFormSet
from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_http_methods, require_safe

from accounts.access import admin_required, basic_user_required
from accounts.models import User
from borrowing.forms import (
    DecisionForm,
    DueDateRevisionForm,
    LoanFilterForm,
    RequestCancellationForm,
    RequestForm,
    RequestHistoryFilterForm,
    RequestItemFormSetFactory,
    RequestQueueForm,
)
from borrowing.models import BorrowRequest, Loan, LoanUnit, RequestStatus
from borrowing.queries import (
    loan_for_request,
    loan_history,
    request_history,
    request_lines,
    request_queue,
)
from borrowing.services import (
    RequestCancellationConflict,
    WorkflowConflict,
    approve_request,
    cancel_request,
    issue_request,
    reject_request,
    revise_due_date,
    submit_request,
)
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
            "active_portal_tab": "request-list",
        },
    )


@require_safe
@basic_user_required
def portal_request_list(request: HttpRequest) -> HttpResponse:
    """List the signed-in borrower's requests with a validated optional status filter."""
    user: User = cast(User, request.user)
    form: RequestHistoryFilterForm = RequestHistoryFilterForm(request.GET)
    requests: QuerySet[BorrowRequest] = (
        request_history(user.pk, form.cleaned_data["status"])
        if form.is_valid()
        else BorrowRequest.objects.none()
    )
    paginator: Paginator[BorrowRequest] = Paginator(requests, 6)
    try:
        page: Page[BorrowRequest] = paginator.page(request.GET.get("page", "1"))
    except (PageNotAnInteger, EmptyPage) as error:
        raise Http404("The requested request-history page does not exist.") from error
    return render(
        request,
        "accounts/portal/request_list.html",
        {"form": form, "page": page, "active_portal_tab": "request-list"},
    )


@require_safe
@basic_user_required
def request_detail(request: HttpRequest, request_id: int) -> HttpResponse:
    """Show one owner's request and any linked issue/return details."""
    user: User = cast(User, request.user)
    borrow_request: BorrowRequest = get_object_or_404(
        request_history(user.pk, ""),
        pk=request_id,
    )
    loan: Loan | None = loan_for_request(user.pk, borrow_request.pk)
    can_cancel: bool = borrow_request.status in (
        RequestStatus.PENDING,
        RequestStatus.APPROVED,
    )
    return render(
        request,
        "accounts/portal/request_detail.html",
        {
            "borrow_request": borrow_request,
            "loan": loan,
            "can_cancel": can_cancel,
            "active_portal_tab": "request-list",
        },
    )


@require_http_methods(["GET", "POST"])
@basic_user_required
def request_cancel(request: HttpRequest, request_id: int) -> HttpResponse:
    """Confirm and execute only the signed-in borrower's eligible cancellation."""
    user: User = cast(User, request.user)
    borrow_request: BorrowRequest = get_object_or_404(
        BorrowRequest.objects.filter(owner_id=user.pk),
        pk=request_id,
    )
    form: RequestCancellationForm = RequestCancellationForm(
        request.POST if request.method == "POST" else None
    )
    if borrow_request.status not in (RequestStatus.PENDING, RequestStatus.APPROVED):
        return render(
            request,
            "accounts/portal/request_cancel.html",
            {
                "borrow_request": borrow_request,
                "error": "Only Pending or Approved requests can be cancelled.",
                "active_portal_tab": "request-list",
            },
            status=409,
        )

    if request.method == "POST" and form.is_valid():
        try:
            cancel_request(owner_id=user.pk, request_id=borrow_request.pk)
        except RequestCancellationConflict as error:
            return render(
                request,
                "accounts/portal/request_cancel.html",
                {
                    "borrow_request": borrow_request,
                    "error": str(error),
                    "active_portal_tab": "request-list",
                },
                status=409,
            )
        except BorrowRequest.DoesNotExist as error:
            raise Http404("The requested borrower request does not exist.") from error
        messages.success(request, f"Request #{borrow_request.pk} was cancelled.")
        return redirect("portal:request-detail", request_id=borrow_request.pk)

    return render(
        request,
        "accounts/portal/request_cancel.html",
        {
            "borrow_request": borrow_request,
            "form": form,
            "active_portal_tab": "request-list",
        },
    )


@require_safe
@basic_user_required
def portal_loan_list(request: HttpRequest) -> HttpResponse:
    """List the signed-in borrower's issued loans and outstanding return progress."""
    user: User = cast(User, request.user)
    loans: QuerySet[Loan] = loan_history(user.pk)
    paginator: Paginator[Loan] = Paginator(loans, 25)
    try:
        page: Page[Loan] = paginator.page(request.GET.get("page", "1"))
    except (PageNotAnInteger, EmptyPage) as error:
        raise Http404("The requested loan-history page does not exist.") from error
    return render(
        request,
        "accounts/portal/loan_list.html",
        {"page": page, "active_portal_tab": "loan-list"},
    )


@require_safe
@basic_user_required
def loan_detail(request: HttpRequest, loan_id: int) -> HttpResponse:
    """Show one owner's loan with its due date and individual unit return states."""
    user: User = cast(User, request.user)
    loan: Loan = get_object_or_404(loan_history(user.pk), pk=loan_id)
    return render(
        request,
        "accounts/portal/loan_detail.html",
        {"loan": loan, "active_portal_tab": "loan-list"},
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
def manage_request_detail(request: HttpRequest, request_id: int) -> HttpResponse:
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


@require_http_methods(["GET", "HEAD", "POST"])
@admin_required
def request_due_date(request: HttpRequest, request_id: int) -> HttpResponse:
    """GET shows the pre-issue due date revision form; POST updates agreed_due_date."""
    borrow_request = get_object_or_404(BorrowRequest.objects.select_related("owner"), pk=request_id)
    initial_data = {
        "agreed_due_date": borrow_request.agreed_due_date,
    }
    form = DueDateRevisionForm(
        request.POST if request.method == "POST" else None,
        initial=initial_data,
    )
    conflict = None
    status = 200

    if request.method == "POST" and form.is_valid():
        try:
            revise_due_date(
                actor_id=cast(User, request.user).pk,
                request_id=borrow_request.pk,
                agreed_due_date=form.cleaned_data["agreed_due_date"],
                reason=form.cleaned_data["reason"],
            )
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
    }
    return render(request, "borrowing/manage/request_due_date.html", context, status=status)


@require_http_methods(["GET", "HEAD", "POST"])
@admin_required
def request_release(request: HttpRequest, request_id: int) -> HttpResponse:
    """GET confirms the equipment release; POST issues the request into an active loan."""
    borrow_request = get_object_or_404(BorrowRequest.objects.select_related("owner"), pk=request_id)
    conflict = None
    status = 200

    if request.method == "POST":
        try:
            loan = issue_request(
                actor_id=cast(User, request.user).pk,
                request_id=borrow_request.pk,
            )
        except WorkflowConflict as error:
            conflict, status = str(error), 409
        else:
            return redirect("borrowing_manage:loan-detail", loan_id=loan.pk)

    context = {
        "borrow_request": borrow_request,
        "lines": request_lines(borrow_request),
        "conflict": conflict,
    }
    return render(request, "borrowing/manage/request_release.html", context, status=status)


@require_safe
@admin_required
def loan_list(request: HttpRequest) -> HttpResponse:
    """Searchable, paginated management list of all issued loans."""
    form = LoanFilterForm(request.GET)
    loans = (
        Loan.objects.select_related("request__owner", "issued_by")
        .prefetch_related(
            Prefetch(
                "units",
                queryset=LoanUnit.objects.select_related("allocation__unit__catalog_item"),
            )
        )
        .order_by("-issued_at", "-pk")
    )

    if form.is_valid():
        q = form.cleaned_data.get("q")
        if q:
            loans = loans.filter(
                Q(request__owner__username__icontains=q)
                | Q(request__owner__first_name__icontains=q)
                | Q(request__owner__last_name__icontains=q)
                | Q(request__owner__email__icontains=q)
                | Q(pk__icontains=q)
                | Q(units__allocation__unit__asset_code__icontains=q)
                | Q(units__allocation__unit__catalog_item__name__icontains=q)
            ).distinct()

        status = form.cleaned_data.get("status")
        if status == "active":
            loans = loans.filter(closed_at__isnull=True)
        elif status == "closed":
            loans = loans.filter(closed_at__isnull=False)

    paginator = Paginator(loans, 25)
    page_number = request.GET.get("page", 1)
    try:
        page_obj = paginator.page(page_number)
    except (PageNotAnInteger, EmptyPage):
        page_obj = paginator.page(1)

    context = {
        "form": form,
        "page_obj": page_obj,
        "loans": page_obj.object_list,
    }
    return render(request, "borrowing/manage/loan_list.html", context)


@require_safe
@admin_required
def manage_loan_detail(request: HttpRequest, loan_id: int) -> HttpResponse:
    """Review one loan: issued units, asset codes, due dates, and print link."""
    loan_units = (
        LoanUnit.objects.select_related("allocation__unit__catalog_item")
        .prefetch_related("return_record")
        .order_by("pk")
    )
    loan = get_object_or_404(
        Loan.objects.select_related("request__owner", "issued_by").prefetch_related(
            Prefetch("units", queryset=loan_units)
        ),
        pk=loan_id,
    )
    context = {
        "loan": loan,
        "units": loan.units.all(),
    }
    return render(request, "borrowing/manage/loan_detail.html", context)


@require_safe
@admin_required
def loan_slip(request: HttpRequest, loan_id: int) -> HttpResponse:
    """Clean, print-ready borrowing slip with borrower details, serials, and sign-offs."""
    loan_units = LoanUnit.objects.select_related("allocation__unit__catalog_item").order_by("pk")
    loan = get_object_or_404(
        Loan.objects.select_related("request__owner", "issued_by").prefetch_related(
            Prefetch("units", queryset=loan_units)
        ),
        pk=loan_id,
    )
    context = {
        "loan": loan,
        "units": loan.units.all(),
    }
    return render(request, "borrowing/manage/loan_slip.html", context)
