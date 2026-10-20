"""Protected administrator release forms, issued-loan pages and printable slips."""

from datetime import date
from typing import cast

from django.contrib import messages
from django.core.exceptions import ValidationError
from django.core.paginator import EmptyPage, Page, PageNotAnInteger, Paginator
from django.db.models import QuerySet
from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_http_methods, require_safe

from accounts.access import admin_required
from accounts.models import User
from borrowing.forms import DueDateRevisionForm, LoanSearchForm, ReleaseConfirmationForm
from borrowing.models import BorrowRequest, Loan, RequestStatus
from borrowing.queries import manage_loan_details, manage_loan_history, request_lines
from borrowing.release_services import release_request, revise_due_date
from borrowing.services import WorkflowConflict


@require_http_methods(["GET", "POST"])
@admin_required
def request_due_date(request: HttpRequest, request_id: int) -> HttpResponse:
    """Confirm an audited pre-issue date revision; GET never writes."""
    borrow_request: BorrowRequest = get_object_or_404(
        BorrowRequest.objects.select_related("owner"), pk=request_id
    )
    form: DueDateRevisionForm = DueDateRevisionForm(
        request.POST if request.method == "POST" else None,
        borrow_request,
        timezone.localdate(),
    )
    conflict: str = ""
    if borrow_request.status != RequestStatus.APPROVED:
        conflict = "Only an Approved request can have its due date revised before issue."
    elif request.method == "POST" and form.is_valid():
        try:
            revise_due_date(
                cast(User, request.user).pk,
                request_id,
                form.cleaned_data["agreed_due_date"],
                form.cleaned_data["reason"],
            )
        except WorkflowConflict as error:
            conflict = str(error)
        except ValidationError as error:
            form.add_error(None, error.messages)
        else:
            messages.success(request, f"Request #{request_id} due date was revised.")
            return redirect("borrowing_manage:request-detail", request_id=request_id)
    return render(
        request,
        "borrowing/manage/request_due_date.html",
        {"borrow_request": borrow_request, "form": form, "conflict": conflict},
        status=409 if conflict else 200,
    )


@require_http_methods(["GET", "POST"])
@admin_required
def request_release(request: HttpRequest, request_id: int) -> HttpResponse:
    """Confirm release; the service rechecks current date, account and reservation state."""
    borrow_request: BorrowRequest = get_object_or_404(
        BorrowRequest.objects.select_related("owner"), pk=request_id
    )
    form: ReleaseConfirmationForm = ReleaseConfirmationForm(
        request.POST if request.method == "POST" else None
    )
    conflict: str = ""
    if borrow_request.status != RequestStatus.APPROVED:
        conflict = "Only an Approved request can be released once."
    elif request.method == "POST" and form.is_valid():
        try:
            loan: Loan = release_request(cast(User, request.user).pk, request_id)
        except WorkflowConflict as error:
            conflict = str(error)
        else:
            messages.success(request, f"Request #{request_id} was released as loan #{loan.pk}.")
            return redirect("borrowing_manage:loan-detail", loan_id=loan.pk)
    return render(
        request,
        "borrowing/manage/request_release.html",
        {
            "borrow_request": borrow_request,
            "form": form,
            "conflict": conflict,
            "lines": request_lines(borrow_request),
        },
        status=409 if conflict else 200,
    )


@require_safe
@admin_required
def loan_list(request: HttpRequest) -> HttpResponse:
    """Search issued loans without exposing an unfiltered result for invalid input."""
    form: LoanSearchForm = LoanSearchForm(request.GET)
    loans: QuerySet[Loan] = (
        manage_loan_history(form.cleaned_data["q"]) if form.is_valid() else Loan.objects.none()
    )
    paginator: Paginator[Loan] = Paginator(loans, 25)
    try:
        page: Page[Loan] = paginator.page(request.GET.get("page", "1"))
    except (PageNotAnInteger, EmptyPage) as error:
        raise Http404("The requested loan page does not exist.") from error
    return render(request, "borrowing/manage/loan_list.html", {"form": form, "page": page})


@require_safe
@admin_required
def loan_detail(request: HttpRequest, loan_id: int) -> HttpResponse:
    """Show issued assets, return progress and the derived overdue label."""
    loan: Loan = get_object_or_404(manage_loan_details(), pk=loan_id)
    today: date = timezone.localdate()
    return render(request, "borrowing/manage/loan_detail.html", {"loan": loan, "today": today})


@require_safe
@admin_required
def loan_slip(request: HttpRequest, loan_id: int) -> HttpResponse:
    """Render a standalone printable document with the same full active-admin boundary."""
    loan: Loan = get_object_or_404(manage_loan_details(), pk=loan_id)
    return render(request, "borrowing/manage/loan_slip.html", {"loan": loan})
