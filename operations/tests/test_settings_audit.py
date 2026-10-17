"""Real PostgreSQL/client checks for operational settings and read-only audit search."""

from datetime import date, datetime, timedelta
from datetime import timezone as datetime_timezone

from django.contrib.auth import SESSION_KEY
from django.core.exceptions import ValidationError
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from accounts.models import User
from borrowing.models import BorrowRequest, RequestItem
from operations.models import AuditAction, AuditActorKind, AuditLog, AuditTarget, SystemSetting
from operations.queries import get_loan_limits
from operations.tests.records import CatalogRecords, create_catalog_records, create_request
from operations.validation import (
    LoanLimits,
    RequestedItem,
    validate_requested_due_date,
    validate_requested_items,
)


class SettingsAuditTests(TestCase):
    records: CatalogRecords

    @classmethod
    def setUpTestData(cls) -> None:
        cls.records = create_catalog_records()

    def setUp(self) -> None:
        self.client.force_login(self.records.admin)

    def test_admin_pages_read_current_data_without_writing(self) -> None:
        setting: SystemSetting = SystemSetting.objects.get(pk=1)
        original_count: int = AuditLog.objects.count()
        response = self.client.get(reverse("operations:settings"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["form"].initial["max_loan_days"], 7)
        self.assertEqual(response.context["form"].initial["max_quantity_per_item"], 3)
        for route in ("operations:settings", "operations:audit-list"):
            self.assertEqual(self.client.head(reverse(route)).status_code, 200)
        audit_response = self.client.get(reverse("operations:audit-list"))
        self.assertEqual(audit_response.status_code, 200)
        self.assertContains(audit_response, 'data-testid="audit-entry-')
        self.assertEqual(AuditLog.objects.count(), original_count)
        self.assertEqual(SystemSetting.objects.get(pk=1).updated_at, setting.updated_at)

    def test_settings_post_uses_server_actor_and_changes_only_future_limits(self) -> None:
        existing_item: RequestItem = create_request(
            self.records.borrower.pk, self.records.item.pk, timezone.now()
        )
        response = self.client.post(
            reverse("operations:settings"),
            {
                "max_loan_days": "2",
                "max_quantity_per_item": "1",
                "updated_by": self.records.borrower.pk,
                "updated_at": "2000-01-01",
                "role": "BASIC_USER",
                "id": "2",
            },
        )
        self.assertRedirects(response, reverse("operations:settings"))
        setting: SystemSetting = SystemSetting.objects.get(pk=1)
        self.assertEqual(setting.updated_by_id, self.records.admin.pk)
        self.assertEqual(timezone.localdate(setting.updated_at), timezone.localdate())
        self.assertEqual(SystemSetting.objects.count(), 1)
        limits: LoanLimits = get_loan_limits()
        self.assertEqual(limits, LoanLimits(max_loan_days=2, max_quantity_per_item=1))
        request: BorrowRequest = BorrowRequest.objects.get(pk=existing_item.request_id)
        self.assertEqual((request.max_loan_days_applied, request.max_quantity_applied), (7, 3))
        submitted_on: date = timezone.localdate()
        self.assertEqual(
            validate_requested_due_date(submitted_on, submitted_on + timedelta(days=2), limits),
            submitted_on + timedelta(days=2),
        )
        with self.assertRaises(ValidationError):
            validate_requested_due_date(submitted_on, submitted_on + timedelta(days=3), limits)
        self.assertEqual(
            validate_requested_items((RequestedItem(self.records.item.pk, 1),), limits),
            (RequestedItem(self.records.item.pk, 1),),
        )
        with self.assertRaises(ValidationError):
            validate_requested_items((RequestedItem(self.records.item.pk, 2),), limits)
        audit: AuditLog = AuditLog.objects.get(action=AuditAction.SETTINGS_UPDATED)
        self.assertEqual(
            (audit.actor_id, audit.target_model, audit.target_id),
            (self.records.admin.pk, AuditTarget.SYSTEM_SETTING, 1),
        )
        self.assertIn("7 -> 2", audit.summary)
        self.assertIn("3 -> 1", audit.summary)
        history = self.client.get(
            reverse("operations:audit-list"), {"action": AuditAction.SETTINGS_UPDATED}
        )
        self.assertEqual(list(history.context["page"]), [audit])

    def test_invalid_settings_show_bound_errors_without_partial_writes(self) -> None:
        for field in ("max_loan_days", "max_quantity_per_item"):
            for value in ("", "0", "-1", "1.5", "2147483648", "invalid"):
                with self.subTest(field=field, value=value):
                    payload: dict[str, str] = {"max_loan_days": "4", "max_quantity_per_item": "2"}
                    payload[field] = value
                    response = self.client.post(reverse("operations:settings"), payload)
                    self.assertEqual(response.status_code, 200)
                    self.assertIn(field, response.context["form"].errors)
                    self.assertContains(response, 'data-testid="settings-errors"')
                    self.assertEqual(get_loan_limits(), LoanLimits(7, 3))
                    self.assertFalse(
                        AuditLog.objects.filter(action=AuditAction.SETTINGS_UPDATED).exists()
                    )

    def test_settings_and_audit_enforce_roles_sessions_csrf_and_methods(self) -> None:
        anonymous: Client = Client()
        for route in ("operations:settings", "operations:audit-list"):
            path: str = reverse(route)
            self.assertRedirects(anonymous.get(path), f"{reverse('accounts:login')}?next={path}")
            self.assertEqual(
                anonymous.post(path, {}).status_code, 302 if route == "operations:settings" else 405
            )
            self.assertEqual(self.client.put(path).status_code, 405)
            self.assertEqual(self.client.delete(path).status_code, 405)
            User.objects.filter(pk=self.records.borrower.pk).update(
                is_staff=True, is_superuser=True
            )
            self.client.force_login(self.records.borrower)
            self.assertEqual(self.client.get(path).status_code, 403)
            self.assertEqual(
                self.client.post(path, {"role": "ADMIN"}).status_code,
                403 if route == "operations:settings" else 405,
            )
            User.objects.filter(pk=self.records.admin.pk).update(is_active=True)
            self.records.admin.refresh_from_db()
            self.client.force_login(self.records.admin)
            User.objects.filter(pk=self.records.admin.pk).update(is_active=False)
            self.assertEqual(self.client.get(path).status_code, 403)
            self.assertNotIn(SESSION_KEY, self.client.session)
        User.objects.filter(pk=self.records.admin.pk).update(is_active=True)
        self.records.admin.refresh_from_db()
        csrf_client: Client = Client(enforce_csrf_checks=True)
        csrf_client.force_login(self.records.admin)
        self.assertEqual(
            csrf_client.post(
                reverse("operations:settings"), {"max_loan_days": 4, "max_quantity_per_item": 2}
            ).status_code,
            403,
        )
        self.assertEqual(self.client.post(reverse("operations:audit-list"), {}).status_code, 405)
        self.assertEqual(get_loan_limits(), LoanLimits(7, 3))
        self.assertFalse(AuditLog.objects.filter(action=AuditAction.SETTINGS_UPDATED).exists())

    def test_audit_filters_reference_action_actor_and_inclusive_campus_dates(self) -> None:
        times: tuple[datetime, ...] = (
            datetime(2026, 1, 1, 15, 59, 59, tzinfo=datetime_timezone.utc),
            datetime(2026, 1, 1, 16, 0, tzinfo=datetime_timezone.utc),
            datetime(2026, 1, 2, 15, 59, 59, tzinfo=datetime_timezone.utc),
            datetime(2026, 1, 2, 16, 0, tzinfo=datetime_timezone.utc),
        )
        entries: list[AuditLog] = AuditLog.objects.bulk_create(
            [
                AuditLog(
                    actor=self.records.admin,
                    actor_kind=AuditActorKind.USER,
                    action=AuditAction.ITEM_UPDATED,
                    occurred_at=occurred_at,
                    target_model=AuditTarget.CATALOG_ITEM,
                    target_id=self.records.item.pk,
                    summary="Fictional item description revised.",
                )
                for occurred_at in times
            ]
        )
        filters: dict[str, str] = {
            "q": f"  inventory.CatalogItem#{self.records.item.pk}  ",
            "action": AuditAction.ITEM_UPDATED,
            "actor": str(self.records.admin.pk),
            "date_from": "2026-01-02",
            "date_to": "2026-01-02",
        }
        response = self.client.get(reverse("operations:audit-list"), filters)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.context["page"]), [entries[2], entries[1]])
        for field, value in (
            ("q", "no-such-reference"),
            ("action", AuditAction.ACCOUNT_UPDATED),
            ("actor", str(self.records.borrower.pk)),
        ):
            with self.subTest(field=field):
                response = self.client.get(
                    reverse("operations:audit-list"), {**filters, field: value}
                )
                self.assertEqual(response.context["page"].paginator.count, 0)
                self.assertContains(response, 'data-testid="audit-empty"')
        response = self.client.get(reverse("operations:audit-list"), {"q": "catalogitem"})
        self.assertEqual(list(response.context["page"]), list(reversed(entries)))
        system_response = self.client.get(
            reverse("operations:audit-list"), {"action": AuditAction.SETTINGS_INITIALIZED}
        )
        self.assertEqual(system_response.context["page"].paginator.count, 1)
        self.assertIsNone(system_response.context["page"][0].actor_id)

    def test_invalid_audit_filters_show_errors_and_do_not_show_unfiltered_data(self) -> None:
        for filters in (
            {"q": "x" * 201},
            {"action": "UNKNOWN_ACTION"},
            {"actor": "0"},
            {"actor": "1.5"},
            {"actor": "9223372036854775808"},
            {"date_from": "2026-02-30"},
            {"date_to": "not-a-date"},
            {"date_from": "2026-02-02", "date_to": "2026-02-01"},
        ):
            with self.subTest(filters=filters):
                response = self.client.get(reverse("operations:audit-list"), filters)
                self.assertEqual(response.status_code, 200)
                self.assertTrue(response.context["form"].errors)
                self.assertContains(response, 'data-testid="audit-errors"')
                self.assertNotContains(response, 'data-testid="audit-table"')
                self.assertEqual(response.context["page"].paginator.count, 0)

    def test_audit_pagination_is_stable_preserves_filters_and_rejects_invalid_pages(self) -> None:
        occurred_at: datetime = timezone.now()
        entries: list[AuditLog] = AuditLog.objects.bulk_create(
            [
                AuditLog(
                    actor=self.records.admin,
                    actor_kind=AuditActorKind.USER,
                    action=AuditAction.ITEM_UPDATED,
                    occurred_at=occurred_at,
                    target_model=AuditTarget.CATALOG_ITEM,
                    target_id=self.records.item.pk,
                    summary="<script>alert('unsafe')</script>",
                )
                for _ in range(26)
            ]
        )
        filters: dict[str, str] = {
            "q": f"inventory.CatalogItem#{self.records.item.pk}",
            "action": AuditAction.ITEM_UPDATED,
            "actor": str(self.records.admin.pk),
            "date_from": timezone.localdate().isoformat(),
            "date_to": timezone.localdate().isoformat(),
        }
        response = self.client.get(reverse("operations:audit-list"), filters)
        self.assertEqual(list(response.context["page"]), list(reversed(entries[1:])))
        self.assertContains(response, "q=inventory.CatalogItem%23")
        self.assertContains(response, f"action={AuditAction.ITEM_UPDATED}")
        self.assertContains(response, f"actor={self.records.admin.pk}")
        self.assertContains(response, f"date_from={filters['date_from']}")
        self.assertContains(response, f"date_to={filters['date_to']}")
        self.assertContains(response, "page=2")
        self.assertContains(response, "&lt;script&gt;")
        self.assertNotContains(response, "<script>alert")
        second_page = self.client.get(reverse("operations:audit-list"), {**filters, "page": "2"})
        self.assertEqual(list(second_page.context["page"]), [entries[0]])
        for page in ("0", "-1", "1.5", "bad", "3"):
            with self.subTest(page=page):
                self.assertEqual(
                    self.client.get(
                        reverse("operations:audit-list"), {**filters, "page": page}
                    ).status_code,
                    404,
                )
