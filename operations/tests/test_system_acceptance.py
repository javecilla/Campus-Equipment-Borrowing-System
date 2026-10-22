"""T22 integrated HTTP lifecycle and complete management-route access checks."""

import csv
import re
from collections.abc import Sequence
from datetime import timedelta
from io import StringIO

from django.contrib.auth import SESSION_KEY
from django.core import serializers
from django.db.models import Model
from django.http import HttpResponse
from django.test import Client, TestCase
from django.urls import URLPattern, URLResolver, get_resolver, reverse
from django.utils import timezone

from accounts.models import User, UserRole
from borrowing.models import BorrowRequest, Loan, RequestStatus, ReturnRecord, UnitAllocation
from borrowing.release_services import release_request
from borrowing.return_services import ReturnInput
from borrowing.services import approve_request, submit_request
from borrowing.tests.test_returns import return_payload
from inventory.models import (
    CatalogItem,
    EquipmentUnit,
    MaintenanceOutcome,
    MaintenanceRecord,
    MaintenanceStatus,
    UnitCondition,
    UnitStatus,
)
from operations.models import AuditAction, AuditLog, SystemSetting
from operations.queries import DashboardCards, ReportTotals
from operations.tests.records import CatalogRecords, create_catalog_records
from operations.validation import RequestedItem


def management_paths(patterns: Sequence[URLPattern | URLResolver], prefix: str) -> tuple[str, ...]:
    """Expand current named path routes with dummy IDs; authorization must precede lookup."""
    paths: list[str] = []
    for pattern in patterns:
        path: str = prefix + str(pattern.pattern)
        if isinstance(pattern, URLResolver):
            paths.extend(management_paths(pattern.url_patterns, path))
        elif path.startswith("manage/"):
            paths.append("/" + re.sub(r"<int:\w+>", "1", path))
    return tuple(paths)


class SystemAcceptanceTests(TestCase):
    records: CatalogRecords
    items: tuple[CatalogItem, ...]

    @classmethod
    def setUpTestData(cls) -> None:
        cls.records = create_catalog_records()
        cls.items = (
            cls.records.item,
            CatalogItem.objects.create(
                category=cls.records.category,
                name="Presentation projector",
                description="Classroom projector with power and HDMI cables.",
            ),
            CatalogItem.objects.create(
                category=cls.records.category,
                name="Wireless microphone",
                description="Microphone with receiver and protective case.",
            ),
        )
        for index, item in enumerate(cls.items[1:], 2):
            EquipmentUnit.objects.create(
                catalog_item=item,
                asset_code=f"T22-UNIT-{index:03d}",
                condition=UnitCondition.GOOD,
                acquired_on=timezone.localdate(),
                status=UnitStatus.AVAILABLE,
            )

    def post_form(self, client: Client, url: str, data: dict[str, str]) -> HttpResponse:
        """Submit the real form with its CSRF cookie, without bypassing middleware."""
        self.assertEqual(client.get(url).status_code, 200)
        return client.post(url, {**data, "csrfmiddlewaretoken": client.cookies["csrftoken"].value})

    def assert_reports(self, client: Client, expected: ReportTotals) -> None:
        """Compare live filtered HTML and downloaded CSV after a committed workflow step."""
        filters: dict[str, str] = {
            "date_from": timezone.localdate().isoformat(),
            "date_to": timezone.localdate().isoformat(),
        }
        report = client.get(reverse("operations:loan-report"), filters)
        self.assertEqual(report.status_code, 200)
        self.assertEqual(report.context["totals"], expected)
        exported = client.get(reverse("operations:loan-export"), filters)
        self.assertEqual(exported.status_code, 200)
        exported_rows: tuple[dict[str, str], ...] = tuple(
            csv.DictReader(StringIO(exported.content.decode("utf-8-sig")))
        )
        rows: tuple[dict[str, str], ...] = exported_rows[:-1]
        totals_row: dict[str, str] = exported_rows[-1]
        self.assertTrue(totals_row["Loan ID"].startswith("TOTALS ("))
        self.assertEqual(int(totals_row["Issued quantity"]), expected.issued_quantity)
        self.assertEqual(int(totals_row["Returned quantity"]), expected.returned_quantity)
        self.assertEqual(int(totals_row["Outstanding quantity"]), expected.outstanding_quantity)
        self.assertEqual(len(rows), expected.loan_count)
        self.assertEqual(sum(int(row["Issued quantity"]) for row in rows), expected.issued_quantity)
        self.assertEqual(
            sum(int(row["Returned quantity"]) for row in rows), expected.returned_quantity
        )
        self.assertEqual(
            sum(int(row["Outstanding quantity"]) for row in rows), expected.outstanding_quantity
        )
        self.assertTrue(all(row["Purpose"].startswith("'=") for row in rows))

    def test_three_item_http_lifecycle_updates_stock_reports_and_repairs(self) -> None:
        borrower = Client(enforce_csrf_checks=True)
        admin = Client(enforce_csrf_checks=True)
        borrower.force_login(self.records.borrower)
        admin.force_login(self.records.admin)
        payload: dict[str, str] = {
            "purpose": "=Media studies presentation and recorded class demonstration",
            "desired_due_date": (timezone.localdate() + timedelta(days=3)).isoformat(),
            "items-TOTAL_FORMS": "3",
            "items-INITIAL_FORMS": "0",
            "items-MIN_NUM_FORMS": "1",
            "items-MAX_NUM_FORMS": "3",
            "owner": str(self.records.admin.pk),
            "status": RequestStatus.RETURNED,
        }
        for index, item in enumerate(self.items):
            payload[f"items-{index}-catalog_item"] = str(item.pk)
            payload[f"items-{index}-quantity"] = "1"
        invalid: dict[str, str] = {**payload, "items-2-quantity": "0"}
        create_url: str = reverse("portal:request-create")
        self.assertEqual(self.post_form(borrower, create_url, invalid).status_code, 200)
        self.assertFalse(BorrowRequest.objects.exists())
        self.assertEqual(self.post_form(borrower, create_url, payload).status_code, 302)
        request: BorrowRequest = BorrowRequest.objects.get()
        self.assertEqual(
            (request.owner_id, request.status, request.items.count()),
            (self.records.borrower.pk, RequestStatus.PENDING, 3),
        )
        approve_url: str = reverse("borrowing_manage:request-approve", args=[request.pk])
        self.assertEqual(
            self.post_form(
                admin,
                approve_url,
                {"reason": "Three-item kit reserved for the classroom presentation."},
            ).status_code,
            302,
        )
        self.assertEqual(EquipmentUnit.objects.filter(status=UnitStatus.RESERVED).count(), 3)
        maintenance_url: str = reverse("inventory_manage:maintenance-create")
        maintenance_payload: dict[str, str] = {
            "unit": str(self.records.unit.pk),
            "problem": "Inspect the loose accessory connector.",
        }
        self.assertEqual(
            self.post_form(admin, maintenance_url, maintenance_payload).status_code, 200
        )
        self.assertFalse(MaintenanceRecord.objects.exists())
        due_url: str = reverse("borrowing_manage:request-due-date", args=[request.pk])
        revised_due: str = (timezone.localdate() + timedelta(days=4)).isoformat()
        self.assertEqual(
            self.post_form(
                admin,
                due_url,
                {
                    "agreed_due_date": revised_due,
                    "reason": "Presentation moved to the next class meeting.",
                },
            ).status_code,
            302,
        )
        release_url: str = reverse("borrowing_manage:request-release", args=[request.pk])
        self.assertEqual(
            self.post_form(
                admin,
                release_url,
                {"issued_by": str(self.records.borrower.pk), "due_date": "2099-01-01"},
            ).status_code,
            302,
        )
        loan: Loan = Loan.objects.get()
        self.assertEqual(
            (loan.issued_by_id, loan.due_date.isoformat()), (self.records.admin.pk, revised_due)
        )
        self.assertEqual(
            admin.post(
                release_url, {"csrfmiddlewaretoken": admin.cookies["csrftoken"].value}
            ).status_code,
            409,
        )
        slip = admin.get(reverse("borrowing_manage:loan-slip", args=[loan.pk]))
        for unit in EquipmentUnit.objects.all():
            self.assertContains(slip, unit.asset_code)
        self.assertEqual(
            self.post_form(admin, maintenance_url, maintenance_payload).status_code, 200
        )
        self.assertFalse(MaintenanceRecord.objects.exists())
        dashboard = admin.get(reverse("operations:dashboard"))
        self.assertEqual(dashboard.context["snapshot"].cards, DashboardCards(0, 0, 1, 0))
        self.assertEqual(dashboard.context["issued_unit_total"], 3)
        self.assert_reports(admin, ReportTotals(1, 3, 0, 3))
        first, second, third = tuple(loan.units.order_by("pk"))
        return_url: str = reverse("borrowing_manage:return-create", args=[loan.pk])
        first_return: dict[str, str] = return_payload(
            (
                ReturnInput(
                    first.pk,
                    UnitCondition.GOOD,
                    "Camera and accessories inspected; complete kit received.",
                    "",
                ),
            )
        )
        self.assertEqual(self.post_form(admin, return_url, first_return).status_code, 302)
        self.assertEqual(
            admin.post(
                return_url,
                {**first_return, "csrfmiddlewaretoken": admin.cookies["csrftoken"].value},
            ).status_code,
            409,
        )
        self.assert_reports(admin, ReportTotals(1, 3, 1, 2))
        loan.refresh_from_db()
        self.assertIsNone(loan.closed_at)
        final_return: dict[str, str] = return_payload(
            (
                ReturnInput(
                    second.pk,
                    UnitCondition.DAMAGED,
                    "Projector received with a loose socket.",
                    "Power socket is loose; inspect before reissue.",
                ),
                ReturnInput(
                    third.pk,
                    UnitCondition.GOOD,
                    "Receiver and microphone checked and complete.",
                    "",
                ),
            )
        )
        self.assertEqual(self.post_form(admin, return_url, final_return).status_code, 302)
        loan.refresh_from_db()
        request.refresh_from_db()
        self.assertIsNotNone(loan.closed_at)
        self.assertEqual(request.status, RequestStatus.RETURNED)
        self.assertEqual(ReturnRecord.objects.count(), 3)
        maintenance: MaintenanceRecord = MaintenanceRecord.objects.get()
        self.assertEqual(maintenance.source_return.loan_unit_id, second.pk)
        self.assertEqual(maintenance.status, MaintenanceStatus.OPEN)
        self.assert_reports(admin, ReportTotals(1, 3, 3, 0))
        close_url: str = reverse("inventory_manage:maintenance-close", args=[maintenance.pk])
        self.assertEqual(
            self.post_form(
                admin,
                close_url,
                {
                    "action": "Secured socket and verified a stable image and power connection.",
                    "outcome": MaintenanceOutcome.AVAILABLE,
                    "repaired_condition": UnitCondition.GOOD,
                },
            ).status_code,
            302,
        )
        self.assertEqual(EquipmentUnit.objects.filter(status=UnitStatus.AVAILABLE).count(), 3)
        self.assertFalse(UnitAllocation.objects.filter(ended_at__isnull=True).exists())
        self.assertEqual(AuditLog.objects.filter(action=AuditAction.UNIT_RETURNED).count(), 3)
        self.assertEqual(
            admin.get(reverse("operations:dashboard")).context["snapshot"].cards,
            DashboardCards(3, 0, 0, 0),
        )
        owner_page = borrower.get(reverse("portal:loan-detail", args=[loan.pk]))
        self.assertEqual(owner_page.status_code, 200)
        self.assertNotContains(owner_page, maintenance.problem)

    def test_every_management_route_rejects_basic_users_and_invalidates_inactive_sessions(
        self,
    ) -> None:
        paths: tuple[str, ...] = management_paths(get_resolver().url_patterns, "")
        self.assertGreater(len(paths), 30)
        models: tuple[type[Model], ...] = (
            BorrowRequest,
            Loan,
            UnitAllocation,
            ReturnRecord,
            EquipmentUnit,
            MaintenanceRecord,
            AuditLog,
            SystemSetting,
        )
        baseline: tuple[str, ...] = tuple(
            serializers.serialize("json", model.objects.order_by("pk")) for model in models
        )
        basic = Client()
        basic.force_login(self.records.borrower)
        for path in paths:
            with self.subTest(path=path):
                self.assertIn(basic.get(path).status_code, (403, 405))
                self.assertIn(basic.post(path, {}).status_code, (403, 405))
        User.objects.filter(pk=self.records.admin.pk).update(is_active=False)
        inactive = Client()
        for path in paths:
            with self.subTest(inactive_path=path):
                inactive.force_login(self.records.admin)
                self.assertEqual(inactive.get(path).status_code, 403)
                self.assertNotIn(SESSION_KEY, inactive.session)
        for model, original in zip(models, baseline, strict=True):
            self.assertEqual(serializers.serialize("json", model.objects.order_by("pk")), original)

    def test_foreign_loan_and_request_routes_are_hidden_and_admin_posts_require_csrf(self) -> None:
        request: BorrowRequest = submit_request(
            self.records.borrower.pk,
            "Cross-owner access check",
            timezone.localdate() + timedelta(days=3),
            (RequestedItem(self.records.item.pk, 1),),
        )
        approve_request(
            self.records.admin.pk, request.pk, "Authorized classroom equipment request."
        )
        loan: Loan = release_request(self.records.admin.pk, request.pk)
        foreign: User = User.objects.create_user(
            username="t22_other_borrower", password=None, role=UserRole.BASIC_USER
        )
        client = Client()
        client.force_login(foreign)
        for route, identifier in (
            ("portal:request-detail", request.pk),
            ("portal:request-cancel", request.pk),
            ("portal:loan-detail", loan.pk),
        ):
            self.assertEqual(client.get(reverse(route, args=[identifier])).status_code, 404)
        self.assertEqual(
            client.post(reverse("portal:request-cancel", args=[request.pk]), {}).status_code, 404
        )
        csrf_client = Client(enforce_csrf_checks=True)
        csrf_client.force_login(self.records.admin)
        original_audits: int = AuditLog.objects.count()
        for path in management_paths(get_resolver().url_patterns, ""):
            with self.subTest(path=path):
                self.assertEqual(csrf_client.post(path, {}).status_code, 403)
        self.assertEqual(AuditLog.objects.count(), original_audits)
        self.assertEqual(ReturnRecord.objects.count(), 0)
        self.assertEqual(Loan.objects.count(), 1)
