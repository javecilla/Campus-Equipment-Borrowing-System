"""Read-only administrator loan reports and CSV exports."""

import csv
from collections.abc import Iterable
from dataclasses import dataclass

from django.core.paginator import EmptyPage, Page, PageNotAnInteger, Paginator
from django.db.models import QuerySet
from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import render
from django.utils import timezone
from django.views.decorators.http import require_GET

from accounts.access import admin_required
from borrowing.models import Loan
from operations.forms import ReportDateFilterForm
from operations.queries import (
    ReportTotals,
    loan_report_rows,
    overdue_report_rows,
    report_totals,
)

REPORT_PAGE_SIZE: int = 25
CSV_FORMULA_PREFIXES: tuple[str, ...] = ("=", "+", "-", "@", "\t", "\r")
LOAN_REPORT_HEADERS: tuple[str, ...] = (
    "Loan ID",
    "Request ID",
    "Borrower",
    "Purpose",
    "Issued on",
    "Due date",
    "Request status",
    "Loan status",
    "Issued quantity",
    "Returned quantity",
    "Outstanding quantity",
)
OVERDUE_REPORT_HEADERS: tuple[str, ...] = (*LOAN_REPORT_HEADERS, "Overdue days")


@dataclass(frozen=True)
class ReportPresentation:
    key: str
    title: str
    description: str
    report_route: str
    export_route: str
    alternate_route: str
    alternate_label: str
    empty_message: str
    show_overdue_days: bool


LOAN_REPORT_PRESENTATION: ReportPresentation = ReportPresentation(
    key="loan-report",
    title="Loan report",
    description="All issued loans. Optional inclusive filters use the stored campus issue date.",
    report_route="operations:loan-report",
    export_route="operations:loan-export",
    alternate_route="operations:overdue-report",
    alternate_label="View overdue report",
    empty_message="No issued loans match these issue-date filters.",
    show_overdue_days=False,
)
OVERDUE_REPORT_PRESENTATION: ReportPresentation = ReportPresentation(
    key="overdue-report",
    title="Overdue report",
    description="Outstanding overdue loans. Optional inclusive filters use the stored campus issue date.",
    report_route="operations:overdue-report",
    export_route="operations:overdue-export",
    alternate_route="operations:loan-report",
    alternate_label="View all loans",
    empty_message="No outstanding overdue loans match these issue-date filters.",
    show_overdue_days=True,
)


def _report_page(loans: QuerySet[Loan], page_value: str, description: str) -> Page[Loan]:
    paginator: Paginator[Loan] = Paginator(loans, REPORT_PAGE_SIZE)
    try:
        return paginator.page(page_value)
    except (PageNotAnInteger, EmptyPage) as error:
        raise Http404(f"The requested {description} page does not exist.") from error


def _loan_state(loan: Loan) -> str:
    if loan.is_overdue:
        return "Overdue"
    if loan.is_active:
        return "Active"
    return "Closed"


def _spreadsheet_safe(value: str | int) -> str | int:
    if isinstance(value, str) and value.startswith(CSV_FORMULA_PREFIXES):
        return f"'{value}"
    return value


def _loan_csv_cells(loan: Loan) -> tuple[str | int, ...]:
    cells: tuple[str | int, ...] = (
        loan.pk,
        loan.request_id,
        loan.request.owner.username,
        loan.request.purpose,
        loan.issued_on.isoformat(),
        loan.due_date.isoformat(),
        loan.request.get_status_display(),
        _loan_state(loan),
        loan.issued_quantity,
        loan.returned_quantity,
        loan.outstanding_quantity,
    )
    return tuple(_spreadsheet_safe(value) for value in cells)


def _csv_response(filename: str) -> HttpResponse:
    response = HttpResponse(content_type="text/csv; charset=utf-8")
    response.headers["Content-Disposition"] = f'attachment; filename="{filename}"'
    response.write("\ufeff")
    return response


def _totals_label(totals: ReportTotals) -> str:
    suffix: str = "loan" if totals.loan_count == 1 else "loans"
    return f"TOTALS ({totals.loan_count} {suffix})"


def _write_loan_csv(
    response: HttpResponse,
    loans: Iterable[Loan],
    totals: ReportTotals,
) -> HttpResponse:
    writer = csv.writer(response)
    writer.writerow(LOAN_REPORT_HEADERS)
    for loan in loans:
        writer.writerow(_loan_csv_cells(loan))
    writer.writerow(
        (
            _totals_label(totals),
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            totals.issued_quantity,
            totals.returned_quantity,
            totals.outstanding_quantity,
        )
    )
    return response


def _write_overdue_csv(
    response: HttpResponse,
    loans: Iterable[Loan],
    totals: ReportTotals,
) -> HttpResponse:
    writer = csv.writer(response)
    writer.writerow(OVERDUE_REPORT_HEADERS)
    for loan in loans:
        writer.writerow((*_loan_csv_cells(loan), loan.overdue_days))
    writer.writerow(
        (
            _totals_label(totals),
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            totals.issued_quantity,
            totals.returned_quantity,
            totals.outstanding_quantity,
            "",
        )
    )
    return response


def _report_context(
    form: ReportDateFilterForm,
    page: Page[Loan],
    totals: ReportTotals,
    presentation: ReportPresentation,
) -> dict[str, object]:
    return {
        "form": form,
        "page": page,
        "totals": totals,
        "filters_valid": form.is_valid(),
        "report_key": presentation.key,
        "report_title": presentation.title,
        "report_description": presentation.description,
        "report_route": presentation.report_route,
        "export_route": presentation.export_route,
        "alternate_route": presentation.alternate_route,
        "alternate_label": presentation.alternate_label,
        "empty_message": presentation.empty_message,
        "show_overdue_days": presentation.show_overdue_days,
        "column_count": 12 if presentation.show_overdue_days else 11,
        "report_navigation_active": True,
    }


def _loan_report_response(request: HttpRequest, form: ReportDateFilterForm) -> HttpResponse:
    loans: QuerySet[Loan] = (
        loan_report_rows(
            form.cleaned_data["date_from"],
            form.cleaned_data["date_to"],
            timezone.localdate(),
        )
        if form.is_valid()
        else Loan.objects.none()
    )
    page: Page[Loan] = _report_page(loans, request.GET.get("page", "1"), "loan report")
    return render(
        request,
        "operations/manage/report.html",
        _report_context(
            form,
            page,
            report_totals(loans),
            LOAN_REPORT_PRESENTATION,
        ),
    )


def _overdue_report_response(request: HttpRequest, form: ReportDateFilterForm) -> HttpResponse:
    loans: QuerySet[Loan] = (
        overdue_report_rows(
            form.cleaned_data["date_from"],
            form.cleaned_data["date_to"],
            timezone.localdate(),
        )
        if form.is_valid()
        else Loan.objects.none()
    )
    page: Page[Loan] = _report_page(loans, request.GET.get("page", "1"), "overdue report")
    return render(
        request,
        "operations/manage/report.html",
        _report_context(
            form,
            page,
            report_totals(loans),
            OVERDUE_REPORT_PRESENTATION,
        ),
    )


@require_GET
@admin_required
def loan_report(request: HttpRequest) -> HttpResponse:
    """Display issued loans with inclusive issue-date filters and exact totals."""
    return _loan_report_response(request, ReportDateFilterForm(request.GET))


@require_GET
@admin_required
def overdue_report(request: HttpRequest) -> HttpResponse:
    """Display currently outstanding overdue loans with the same date contract."""
    return _overdue_report_response(request, ReportDateFilterForm(request.GET))


@require_GET
@admin_required
def loan_export(request: HttpRequest) -> HttpResponse:
    """Download the complete filtered loan report as spreadsheet-safe UTF-8 CSV."""
    form = ReportDateFilterForm(request.GET)
    if not form.is_valid():
        return _loan_report_response(request, form)
    loans: QuerySet[Loan] = loan_report_rows(
        form.cleaned_data["date_from"],
        form.cleaned_data["date_to"],
        timezone.localdate(),
    )
    return _write_loan_csv(_csv_response("loan-report.csv"), loans, report_totals(loans))


@require_GET
@admin_required
def overdue_export(request: HttpRequest) -> HttpResponse:
    """Download the complete filtered overdue report as spreadsheet-safe UTF-8 CSV."""
    form = ReportDateFilterForm(request.GET)
    if not form.is_valid():
        return _overdue_report_response(request, form)
    loans: QuerySet[Loan] = overdue_report_rows(
        form.cleaned_data["date_from"],
        form.cleaned_data["date_to"],
        timezone.localdate(),
    )
    return _write_overdue_csv(_csv_response("overdue-report.csv"), loans, report_totals(loans))
