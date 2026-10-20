"""T19 PostgreSQL-backed administrator loan and overdue reporting checks."""

import codecs
import csv
import io
import re
from datetime import date, datetime, time, timedelta

from django.contrib.auth import SESSION_KEY
from django.db import connection
from django.test import Client, TestCase
from django.test.utils import CaptureQueriesContext
from django.urls import reverse
from django.utils import timezone

from accounts.models import User
from borrowing.models import (
    BorrowRequest,
    Loan,
    LoanUnit,
    RequestItem,
    RequestStatus,
    ReturnRecord,
    UnitAllocation,
)
from inventory.models import EquipmentUnit, UnitCondition, UnitStatus
from operations.queries import (
    ReportTotals,
    loan_report_rows,
    overdue_report_rows,
    report_totals,
)
from operations.tests.records import CatalogRecords, create_catalog_records

REPORT_ROUTES: tuple[str, ...] = (
    "operations:loan-report",
    "operations:loan-export",
    "operations:overdue-report",
    "operations:overdue-export",
)


def _campus_datetime(value: date, hour: int) -> datetime:
    return timezone.make_aware(datetime.combine(value, time(hour=hour)))


def create_report_loan(
    records: CatalogRecords,
    suffix: str,
    issued_on: date,
    due_date: date,
    quantity: int,
    returned_count: int,
    request_status: RequestStatus,
    purpose: str,
) -> Loan:
    """Create internally consistent issued/return records for read-only report checks."""
    issued_at: datetime = _campus_datetime(issued_on, 9)
    submitted_on: date = issued_on - timedelta(days=1)
    borrow_request: BorrowRequest = BorrowRequest.objects.create(
        owner=records.borrower,
        purpose=purpose,
        submitted_at=_campus_datetime(submitted_on, 9),
        submitted_on=submitted_on,
        desired_due_date=due_date,
        agreed_due_date=due_date,
        max_loan_days_applied=7,
        max_quantity_applied=max(3, quantity),
        status=request_status,
        decided_by=records.admin,
        decided_at=issued_at,
        decision_reason="Fictional T19 report approval",
    )
    request_item: RequestItem = RequestItem.objects.create(
        request=borrow_request,
        catalog_item=records.item,
        quantity=quantity,
    )
    returned_at: datetime = issued_at + timedelta(days=1)
    loan: Loan = Loan.objects.create(
        request=borrow_request,
        issued_by=records.admin,
        issued_at=issued_at,
        issued_on=issued_on,
        due_date=due_date,
        closed_at=returned_at if returned_count == quantity else None,
    )
    for index in range(quantity):
        is_returned: bool = index < returned_count
        unit: EquipmentUnit = EquipmentUnit.objects.create(
            catalog_item=records.item,
            asset_code=f"T19-{suffix}-{index + 1:02d}",
            condition=UnitCondition.GOOD,
            acquired_on=issued_on - timedelta(days=1),
            status=UnitStatus.AVAILABLE if is_returned else UnitStatus.ISSUED,
            internal_notes="",
        )
        allocation: UnitAllocation = UnitAllocation.objects.create(
            request_item=request_item,
            unit=unit,
            allocated_at=issued_at - timedelta(hours=1),
            allocated_by=records.admin,
            released_at=issued_at,
            ended_at=returned_at if is_returned else None,
        )
        loan_unit: LoanUnit = LoanUnit.objects.create(loan=loan, allocation=allocation)
        if is_returned:
            ReturnRecord.objects.create(
                loan_unit=loan_unit,
                returned_at=returned_at,
                returned_condition=UnitCondition.GOOD,
                received_by=records.admin,
                notes="Fictional T19 report return",
            )
    return loan


def _csv_rows(response) -> list[list[str]]:
    payload: str = response.content.decode("utf-8-sig")
    return list(csv.reader(io.StringIO(payload, newline="")))


class ReportIntegrationTests(TestCase):
    records: CatalogRecords
    active_loan: Loan
    partial_overdue_loan: Loan
    returned_loan: Loan
    boundary_loan: Loan
    today: date = timezone.localdate()

    @classmethod
    def setUpTestData(cls) -> None:
        cls.records = create_catalog_records()
        cls.active_loan = create_report_loan(
            cls.records,
            "ACTIVE",
            cls.today - timedelta(days=2),
            cls.today + timedelta(days=1),
            2,
            0,
            RequestStatus.ISSUED,
            "Active classroom equipment loan",
        )
        cls.partial_overdue_loan = create_report_loan(
            cls.records,
            "PARTIAL",
            cls.today - timedelta(days=8),
            cls.today - timedelta(days=2),
            3,
            1,
            RequestStatus.PARTIALLY_RETURNED,
            '=SUM(1,1), "quoted"\nUnicode Ñ purpose',
        )
        cls.returned_loan = create_report_loan(
            cls.records,
            "RETURNED",
            cls.today - timedelta(days=6),
            cls.today - timedelta(days=1),
            2,
            2,
            RequestStatus.RETURNED,
            "Fully returned equipment",
        )
        cls.boundary_loan = create_report_loan(
            cls.records,
            "BOUNDARY",
            cls.today,
            cls.today + timedelta(days=1),
            1,
            0,
            RequestStatus.ISSUED,
            "Inclusive date boundary",
        )

    def setUp(self) -> None:
        self.client.force_login(self.records.admin)

    def test_active_admin_access_and_get_only_methods_for_every_endpoint(self) -> None:
        for route in REPORT_ROUTES:
            url: str = reverse(route)
            with self.subTest(route=route):
                response = self.client.get(url)
                self.assertEqual(response.status_code, 200)
                if route.endswith("export"):
                    self.assertEqual(response["Content-Type"], "text/csv; charset=utf-8")
                else:
                    self.assertTemplateUsed(response, "operations/manage/report.html")
                    self.assertContains(response, 'data-testid="nav-manage-reports"')
                    self.assertContains(response, 'aria-current="page"')
                for method in (
                    self.client.head,
                    self.client.post,
                    self.client.put,
                    self.client.patch,
                    self.client.delete,
                    self.client.options,
                ):
                    self.assertEqual(method(url).status_code, 405)

    def test_anonymous_basic_user_and_inactive_admin_are_denied_everywhere(self) -> None:
        anonymous = Client()
        for route in REPORT_ROUTES:
            url: str = reverse(route)
            with self.subTest(route=route, role="anonymous"):
                self.assertRedirects(anonymous.get(url), f"{reverse('accounts:login')}?next={url}")
            self.client.force_login(self.records.borrower)
            with self.subTest(route=route, role="basic"):
                self.assertEqual(self.client.get(url).status_code, 403)
            User.objects.filter(pk=self.records.admin.pk).update(is_active=False)
            self.records.admin.refresh_from_db()
            self.client.force_login(self.records.admin)
            with self.subTest(route=route, role="inactive-admin"):
                self.assertEqual(self.client.get(url).status_code, 403)
                self.assertNotIn(SESSION_KEY, self.client.session)
            User.objects.filter(pk=self.records.admin.pk).update(is_active=True)
            self.records.admin.refresh_from_db()

    def test_inclusive_and_missing_date_bounds_filter_on_issue_date(self) -> None:
        date_from: date = self.returned_loan.issued_on
        date_to: date = self.active_loan.issued_on
        response = self.client.get(
            reverse("operations:loan-report"),
            {"date_from": date_from.isoformat(), "date_to": date_to.isoformat()},
        )
        self.assertEqual(
            [loan.pk for loan in response.context["page"]],
            [self.active_loan.pk, self.returned_loan.pk],
        )
        start_only = self.client.get(
            reverse("operations:loan-report"), {"date_from": self.today.isoformat()}
        )
        self.assertEqual([loan.pk for loan in start_only.context["page"]], [self.boundary_loan.pk])
        end_only = self.client.get(
            reverse("operations:loan-report"),
            {"date_to": self.partial_overdue_loan.issued_on.isoformat()},
        )
        self.assertEqual(
            [loan.pk for loan in end_only.context["page"]],
            [self.partial_overdue_loan.pk],
        )
        unbounded = self.client.get(reverse("operations:loan-report"))
        self.assertEqual(unbounded.context["page"].paginator.count, 4)

    def test_invalid_reversed_and_forged_filters_never_expose_unfiltered_rows(self) -> None:
        for route in REPORT_ROUTES:
            for filters in (
                {"date_from": "2026-02-30"},
                {"date_to": "not-a-date"},
                {"date_from": self.today.isoformat(), "date_to": "2026-01-01"},
            ):
                with self.subTest(route=route, filters=filters):
                    response = self.client.get(reverse(route), filters)
                    self.assertEqual(response.status_code, 200)
                    self.assertEqual(response["Content-Type"], "text/html; charset=utf-8")
                    self.assertTrue(response.context["form"].errors)
                    self.assertContains(
                        response, f'data-testid="{response.context["report_key"]}-errors"'
                    )
                    self.assertNotContains(
                        response, f'data-testid="{response.context["report_key"]}-table"'
                    )
        forged = self.client.get(
            reverse("operations:overdue-report"),
            {"status": RequestStatus.RETURNED, "outstanding_quantity": "0"},
        )
        self.assertEqual(
            [loan.pk for loan in forged.context["page"]], [self.partial_overdue_loan.pk]
        )

    def test_rows_statuses_and_totals_use_exact_return_record_counts(self) -> None:
        self.assertEqual(connection.vendor, "postgresql")
        loans = loan_report_rows(None, None, self.today)
        by_id: dict[int, Loan] = {loan.pk: loan for loan in loans}
        self.assertEqual(len(by_id), 4)
        self.assertEqual(
            (
                by_id[self.active_loan.pk].issued_quantity,
                by_id[self.active_loan.pk].returned_quantity,
                by_id[self.active_loan.pk].outstanding_quantity,
                by_id[self.active_loan.pk].is_active,
                by_id[self.active_loan.pk].is_overdue,
            ),
            (2, 0, 2, True, False),
        )
        self.assertEqual(
            (
                by_id[self.partial_overdue_loan.pk].issued_quantity,
                by_id[self.partial_overdue_loan.pk].returned_quantity,
                by_id[self.partial_overdue_loan.pk].outstanding_quantity,
                by_id[self.partial_overdue_loan.pk].is_active,
                by_id[self.partial_overdue_loan.pk].is_overdue,
                by_id[self.partial_overdue_loan.pk].overdue_days,
            ),
            (3, 1, 2, True, True, 2),
        )
        self.assertEqual(
            (
                by_id[self.returned_loan.pk].issued_quantity,
                by_id[self.returned_loan.pk].returned_quantity,
                by_id[self.returned_loan.pk].outstanding_quantity,
                by_id[self.returned_loan.pk].is_active,
                by_id[self.returned_loan.pk].is_overdue,
            ),
            (2, 2, 0, False, False),
        )
        self.assertEqual(report_totals(loans), ReportTotals(4, 8, 3, 5))

        overdue = overdue_report_rows(None, None, self.today)
        self.assertEqual(list(overdue.values_list("pk", flat=True)), [self.partial_overdue_loan.pk])
        self.assertEqual(report_totals(overdue), ReportTotals(1, 3, 1, 2))

    def test_html_reports_render_correct_identifiers_statuses_quantities_and_empty_states(
        self,
    ) -> None:
        response = self.client.get(reverse("operations:loan-report"))
        self.assertContains(response, f"#{self.active_loan.pk}")
        self.assertContains(response, f"#{self.active_loan.request_id}")
        self.assertContains(response, self.records.borrower.username)
        self.assertContains(
            response,
            f"{self.active_loan.issued_on:%b} {self.active_loan.issued_on.day}, "
            f"{self.active_loan.issued_on.year}",
        )
        self.assertContains(
            response,
            f"{self.active_loan.due_date:%b} {self.active_loan.due_date.day}, "
            f"{self.active_loan.due_date.year}",
        )
        self.assertContains(response, "Partially returned")
        self.assertContains(response, "Returned")
        self.assertContains(response, "Active")
        self.assertContains(response, "Closed")
        self.assertContains(response, "Overdue")
        self.assertEqual(response.context["totals"], ReportTotals(4, 8, 3, 5))

        empty_filters = {"date_from": "2000-01-01", "date_to": "2000-01-02"}
        for route, message in (
            ("operations:loan-report", "No issued loans match these issue-date filters."),
            (
                "operations:overdue-report",
                "No outstanding overdue loans match these issue-date filters.",
            ),
        ):
            with self.subTest(route=route):
                empty = self.client.get(reverse(route), empty_filters)
                self.assertEqual(empty.context["totals"], ReportTotals(0, 0, 0, 0))
                self.assertContains(empty, message)

    def test_pagination_preserves_date_filters_and_rejects_invalid_pages(self) -> None:
        for index in range(22):
            create_report_loan(
                self.records,
                f"PAGE-{index:02d}",
                self.today - timedelta(days=1),
                self.today + timedelta(days=1),
                1,
                0,
                RequestStatus.ISSUED,
                f"Pagination loan {index + 1}",
            )
        filters: dict[str, str] = {
            "date_from": (self.today - timedelta(days=30)).isoformat(),
            "date_to": self.today.isoformat(),
        }
        response = self.client.get(reverse("operations:loan-report"), filters)
        self.assertEqual(len(response.context["page"]), 25)
        self.assertEqual(response.context["page"].paginator.count, 26)
        self.assertContains(response, f"date_from={filters['date_from']}")
        self.assertContains(response, f"date_to={filters['date_to']}")
        self.assertContains(response, "page=2")
        second = self.client.get(reverse("operations:loan-report"), {**filters, "page": "2"})
        self.assertEqual(len(second.context["page"]), 1)
        for page in ("0", "-1", "1.5", "bad", "3"):
            with self.subTest(page=page):
                self.assertEqual(
                    self.client.get(
                        reverse("operations:loan-report"), {**filters, "page": page}
                    ).status_code,
                    404,
                )

    def test_csv_matches_html_filters_order_and_totals_for_both_reports(self) -> None:
        filters: dict[str, str] = {
            "date_from": (self.today - timedelta(days=8)).isoformat(),
            "date_to": (self.today - timedelta(days=2)).isoformat(),
        }
        for report_route, export_route in (
            ("operations:loan-report", "operations:loan-export"),
            ("operations:overdue-report", "operations:overdue-export"),
        ):
            with self.subTest(report=report_route):
                html = self.client.get(reverse(report_route), filters)
                export = self.client.get(reverse(export_route), filters)
                rows = _csv_rows(export)
                html_loans = list(html.context["page"].paginator.object_list)
                self.assertEqual(
                    [int(row[0]) for row in rows[1:-1]], [loan.pk for loan in html_loans]
                )
                rows_by_id: dict[int, list[str]] = {int(row[0]): row for row in rows[1:-1]}
                partial_row: list[str] = rows_by_id[self.partial_overdue_loan.pk]
                self.assertEqual(
                    partial_row[:11],
                    [
                        str(self.partial_overdue_loan.pk),
                        str(self.partial_overdue_loan.request_id),
                        self.records.borrower.username,
                        '\'=SUM(1,1), "quoted"\nUnicode Ñ purpose',
                        self.partial_overdue_loan.issued_on.isoformat(),
                        self.partial_overdue_loan.due_date.isoformat(),
                        "Partially returned",
                        "Overdue",
                        "3",
                        "1",
                        "2",
                    ],
                )
                if report_route == "operations:overdue-report":
                    self.assertEqual(partial_row[11], "2")
                totals: ReportTotals = html.context["totals"]
                suffix: str = "loan" if totals.loan_count == 1 else "loans"
                self.assertEqual(rows[-1][0], f"TOTALS ({totals.loan_count} {suffix})")
                self.assertEqual(
                    tuple(int(value) for value in rows[-1][8:11]),
                    (
                        totals.issued_quantity,
                        totals.returned_quantity,
                        totals.outstanding_quantity,
                    ),
                )

    def test_csv_is_utf8_quoted_and_protects_every_formula_prefix(self) -> None:
        dangerous_purposes: tuple[str, ...] = (
            "=formula",
            "+formula",
            "-formula",
            "@formula",
            "\tformula",
            "\rformula",
        )
        created: list[Loan] = []
        for index, purpose in enumerate(dangerous_purposes):
            created.append(
                create_report_loan(
                    self.records,
                    f"SAFE-{index}",
                    self.today - timedelta(days=1),
                    self.today + timedelta(days=1),
                    1,
                    0,
                    RequestStatus.ISSUED,
                    purpose,
                )
            )
        response = self.client.get(reverse("operations:loan-export"))
        self.assertTrue(response.content.startswith(codecs.BOM_UTF8))
        rows_by_id: dict[int, list[str]] = {int(row[0]): row for row in _csv_rows(response)[1:-1]}
        for loan, purpose in zip(created, dangerous_purposes, strict=True):
            self.assertEqual(rows_by_id[loan.pk][3], f"'{purpose}")
        self.assertEqual(
            rows_by_id[self.partial_overdue_loan.pk][3],
            '\'=SUM(1,1), "quoted"\nUnicode Ñ purpose',
        )

    def test_csv_headers_content_types_and_filenames_are_stable(self) -> None:
        for route, filename, expected_header in (
            (
                "operations:loan-export",
                "loan-report.csv",
                "Loan ID,Request ID,Borrower,Purpose,Issued on,Due date,Request status,Loan status,Issued quantity,Returned quantity,Outstanding quantity",
            ),
            (
                "operations:overdue-export",
                "overdue-report.csv",
                "Loan ID,Request ID,Borrower,Purpose,Issued on,Due date,Request status,Loan status,Issued quantity,Returned quantity,Outstanding quantity,Overdue days",
            ),
        ):
            with self.subTest(route=route):
                response = self.client.get(reverse(route))
                self.assertEqual(response["Content-Type"], "text/csv; charset=utf-8")
                self.assertEqual(
                    response["Content-Disposition"], f'attachment; filename="{filename}"'
                )
                self.assertEqual(
                    response.content.decode("utf-8-sig").splitlines()[0], expected_header
                )

    def test_report_pages_and_exports_issue_only_select_queries(self) -> None:
        before: tuple[int, int, int, int, list[tuple[int, str]]] = (
            BorrowRequest.objects.count(),
            Loan.objects.count(),
            LoanUnit.objects.count(),
            ReturnRecord.objects.count(),
            list(BorrowRequest.objects.order_by("pk").values_list("pk", "status")),
        )
        for route in REPORT_ROUTES:
            with self.subTest(route=route), CaptureQueriesContext(connection) as captured:
                response = self.client.get(reverse(route))
                self.assertEqual(response.status_code, 200)
            write_queries: list[str] = [
                query["sql"]
                for query in captured.captured_queries
                if re.match(r"\s*(INSERT|UPDATE|DELETE|ALTER|CREATE|DROP)\b", query["sql"], re.I)
            ]
            self.assertEqual(write_queries, [])
        after: tuple[int, int, int, int, list[tuple[int, str]]] = (
            BorrowRequest.objects.count(),
            Loan.objects.count(),
            LoanUnit.objects.count(),
            ReturnRecord.objects.count(),
            list(BorrowRequest.objects.order_by("pk").values_list("pk", "status")),
        )
        self.assertEqual(after, before)
