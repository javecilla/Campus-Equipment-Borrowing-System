"""PostgreSQL integration coverage for borrower request submission."""

from datetime import date, timedelta

from django.contrib.auth import SESSION_KEY
from django.core.exceptions import PermissionDenied, ValidationError
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from accounts.models import User, UserRole
from borrowing.models import BorrowRequest, RequestItem, RequestStatus
from borrowing.services import submit_request
from inventory.models import CatalogItem, Category
from operations.models import SystemSetting
from operations.tests.records import CatalogRecords, create_catalog_records
from operations.validation import RequestedItem


class BorrowRequestSubmissionTests(TestCase):
    records: CatalogRecords
    items: tuple[CatalogItem, ...]

    @classmethod
    def setUpTestData(cls) -> None:
        cls.records = create_catalog_records()
        cls.items = (
            cls.records.item,
            CatalogItem.objects.create(
                category=cls.records.category,
                name="Test projector",
                description="Projector for integration checks.",
            ),
            CatalogItem.objects.create(
                category=cls.records.category,
                name="Test microphone",
                description="Microphone for integration checks.",
            ),
        )
        cls.inactive_borrower = User.objects.create_user(
            username="inactive_borrower",
            password="Correct-Horse-Battery-Staple-2026!",
            first_name="Fictional",
            last_name="Inactive",
            email="inactive@example.invalid",
            role=UserRole.BASIC_USER,
            is_active=False,
        )

    def setUp(self) -> None:
        self.client.force_login(self.records.borrower)

    def post_data(
        self,
        rows: tuple[tuple[int, str], ...],
        *,
        purpose: str = "Fictional classroom activity",
        due_date: date | None = None,
        total_forms: int = 3,
        initial_forms: int = 0,
    ) -> dict[str, str]:
        data: dict[str, str] = {
            "purpose": purpose,
            "desired_due_date": (due_date or timezone.localdate() + timedelta(days=3)).isoformat(),
            "items-TOTAL_FORMS": str(total_forms),
            "items-INITIAL_FORMS": str(initial_forms),
            "items-MIN_NUM_FORMS": "1",
            "items-MAX_NUM_FORMS": "3",
        }
        for index, (item_id, quantity) in enumerate(rows):
            data[f"items-{index}-catalog_item"] = str(item_id)
            data[f"items-{index}-quantity"] = quantity
        return data

    def test_request_form_is_available_only_to_active_basic_users(self) -> None:
        path: str = reverse("portal:request-create")
        response = self.client.get(path)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'data-testid="request-create-page"')
        self.assertContains(response, 'name="items-TOTAL_FORMS"')
        self.assertContains(response, "Maximum per item: 3.")
        self.assertContains(response, "Test camera (Test cameras)")
        self.assertEqual(len(response.context["item_formset"].forms), 3)

        anonymous: Client = Client()
        self.assertRedirects(
            anonymous.get(path),
            f"{reverse('accounts:login')}?next={path}",
        )
        self.client.force_login(self.records.admin)
        self.assertEqual(self.client.get(path).status_code, 403)

        self.client.force_login(self.inactive_borrower)
        self.assertEqual(self.client.get(path).status_code, 403)
        self.assertNotIn(SESSION_KEY, self.client.session)

    def test_valid_request_creates_pending_rows_and_snapshots_limits(self) -> None:
        SystemSetting.objects.filter(pk=1).update(
            max_loan_days=10,
            max_quantity_per_item=4,
        )
        due_date: date = timezone.localdate() + timedelta(days=9)
        payload: dict[str, str] = self.post_data(
            (
                (self.items[0].pk, "2"),
                (self.items[1].pk, "3"),
                (self.items[2].pk, "4"),
            ),
            due_date=due_date,
        )
        payload.update(
            {
                "owner": str(self.records.admin.pk),
                "status": RequestStatus.APPROVED,
                "submitted_on": "2000-01-01",
                "max_loan_days_applied": "1",
                "max_quantity_applied": "1",
                "decided_by": str(self.records.admin.pk),
            }
        )

        response = self.client.post(reverse("portal:request-create"), payload)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], reverse("portal:request-list"))

        borrow_request: BorrowRequest = BorrowRequest.objects.get()
        self.assertEqual(borrow_request.owner_id, self.records.borrower.pk)
        self.assertEqual(borrow_request.purpose, "Fictional classroom activity")
        self.assertEqual(borrow_request.submitted_on, timezone.localdate())
        self.assertEqual(borrow_request.desired_due_date, due_date)
        self.assertEqual(borrow_request.agreed_due_date, due_date)
        self.assertEqual(borrow_request.max_loan_days_applied, 10)
        self.assertEqual(borrow_request.max_quantity_applied, 4)
        self.assertEqual(borrow_request.status, RequestStatus.PENDING)
        self.assertIsNone(borrow_request.decided_by_id)
        self.assertEqual(
            list(
                RequestItem.objects.filter(request=borrow_request)
                .order_by("catalog_item_id")
                .values_list("catalog_item_id", "quantity")
            ),
            [(item.pk, quantity) for item, quantity in zip(self.items, (2, 3, 4), strict=True)],
        )

        confirmation = self.client.get(reverse("portal:request-list"))
        self.assertContains(confirmation, "was submitted for administrator review.")
        self.assertContains(confirmation, 'data-testid="request-create-link"')

    def test_invalid_third_row_leaves_no_request_or_request_items(self) -> None:
        response = self.client.post(
            reverse("portal:request-create"),
            self.post_data(
                (
                    (self.items[0].pk, "1"),
                    (self.items[1].pk, "1"),
                    (self.items[2].pk, "0"),
                )
            ),
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("quantity", response.context["item_formset"].forms[2].errors)
        self.assertFalse(BorrowRequest.objects.exists())
        self.assertFalse(RequestItem.objects.exists())

    def test_incomplete_duplicate_and_over_limit_rows_do_not_write(self) -> None:
        cases: tuple[tuple[tuple[tuple[int, str], ...], str], ...] = (
            (((self.items[0].pk, "1"), (self.items[1].pk, "")), "quantity"),
            (((self.items[0].pk, "1"), (self.items[0].pk, "2")), "non_form_errors"),
            (((self.items[0].pk, "4"),), "quantity"),
        )
        for rows, expected_error in cases:
            with self.subTest(rows=rows):
                response = self.client.post(
                    reverse("portal:request-create"),
                    self.post_data(rows),
                )
                self.assertEqual(response.status_code, 200)
                if expected_error == "non_form_errors":
                    self.assertTrue(response.context["item_formset"].non_form_errors())
                else:
                    self.assertTrue(
                        any(
                            expected_error in form.errors
                            for form in response.context["item_formset"]
                        )
                    )
                self.assertFalse(BorrowRequest.objects.exists())
                self.assertFalse(RequestItem.objects.exists())

    def test_invalid_dates_purpose_and_formset_bounds_do_not_write(self) -> None:
        valid_rows: tuple[tuple[int, str], ...] = ((self.items[0].pk, "1"),)
        invalid_submissions: tuple[dict[str, str], ...] = (
            self.post_data(valid_rows, purpose="   "),
            self.post_data(valid_rows, due_date=timezone.localdate()),
            self.post_data(
                valid_rows,
                due_date=timezone.localdate() + timedelta(days=8),
            ),
            self.post_data(valid_rows, total_forms=4),
            self.post_data(valid_rows, initial_forms=1),
        )
        for payload in invalid_submissions:
            with self.subTest(payload=payload):
                response = self.client.post(reverse("portal:request-create"), payload)
                self.assertEqual(response.status_code, 200)
                self.assertFalse(BorrowRequest.objects.exists())
                self.assertFalse(RequestItem.objects.exists())

    def test_direct_service_rechecks_role_and_locked_catalog_eligibility(self) -> None:
        due_date: date = timezone.localdate() + timedelta(days=3)
        requested_items: tuple[RequestedItem, ...] = (RequestedItem(self.items[0].pk, 1),)
        with self.assertRaises(PermissionDenied):
            submit_request(
                owner_id=self.records.admin.pk,
                purpose="Fictional test",
                desired_due_date=due_date,
                items=requested_items,
            )

        CatalogItem.objects.filter(pk=self.items[0].pk).update(is_archived=True)
        with self.assertRaises(ValidationError):
            submit_request(
                owner_id=self.records.borrower.pk,
                purpose="Fictional test",
                desired_due_date=due_date,
                items=requested_items,
            )
        CatalogItem.objects.filter(pk=self.items[0].pk).update(is_archived=False)
        Category.objects.filter(pk=self.records.category.pk).update(is_archived=True)
        with self.assertRaises(ValidationError):
            submit_request(
                owner_id=self.records.borrower.pk,
                purpose="Fictional test",
                desired_due_date=due_date,
                items=requested_items,
            )
        self.assertFalse(BorrowRequest.objects.exists())
        self.assertFalse(RequestItem.objects.exists())

    def test_endpoint_enforces_methods_and_csrf(self) -> None:
        path: str = reverse("portal:request-create")
        self.assertEqual(self.client.put(path).status_code, 405)

        csrf_client: Client = Client(enforce_csrf_checks=True)
        csrf_client.force_login(self.records.borrower)
        self.assertEqual(
            csrf_client.post(path, self.post_data(((self.items[0].pk, "1"),))).status_code,
            403,
        )
        self.assertFalse(BorrowRequest.objects.exists())
        self.assertFalse(RequestItem.objects.exists())
