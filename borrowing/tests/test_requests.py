"""Tests for the administrator request queue, detail page, approval and rejection."""

from datetime import timedelta

from django.core.exceptions import PermissionDenied, ValidationError
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from accounts.models import User
from borrowing.models import BorrowRequest, RequestItem, RequestStatus, UnitAllocation
from borrowing.services import WorkflowConflict, approve_request, reject_request
from inventory.models import CatalogItem, Category, EquipmentUnit, UnitCondition, UnitStatus
from operations.models import AuditAction, AuditLog
from operations.tests.records import CatalogRecords, create_catalog_records


def make_units(item: CatalogItem, count: int) -> list[EquipmentUnit]:
    return [
        EquipmentUnit.objects.create(
            catalog_item=item,
            asset_code=f"T13-{item.pk}-{number}",
            condition=UnitCondition.GOOD,
            acquired_on=timezone.localdate(),
            status=UnitStatus.AVAILABLE,
        )
        for number in range(1, count + 1)
    ]


def make_request(
    owner: User, item: CatalogItem, quantity: int = 1, status: str = RequestStatus.PENDING
) -> BorrowRequest:
    today = timezone.localdate()
    due = today + timedelta(days=3)
    borrow_request = BorrowRequest.objects.create(
        owner=owner,
        purpose="Class demonstration",
        submitted_at=timezone.now(),
        submitted_on=today,
        desired_due_date=due,
        agreed_due_date=due,
        max_loan_days_applied=7,
        max_quantity_applied=3,
        status=status,
    )
    RequestItem.objects.create(request=borrow_request, catalog_item=item, quantity=quantity)
    return borrow_request


class RequestTestBase(TestCase):
    records: CatalogRecords
    category: Category
    item: CatalogItem

    @classmethod
    def setUpTestData(cls) -> None:
        cls.records = create_catalog_records()
        cls.category = Category.objects.create(name="T13 Category", description="T13 tests")
        cls.item = CatalogItem.objects.create(
            category=cls.category, name="T13 Projector", description="Projector for T13 tests."
        )

    def unit_count(self, status: str) -> int:
        return EquipmentUnit.objects.filter(catalog_item=self.item, status=status).count()


class ApprovalServiceTests(RequestTestBase):
    def test_happy_path_reserves_units_and_writes_audit(self) -> None:
        make_units(self.item, 3)
        borrow_request = make_request(self.records.borrower, self.item, quantity=2)

        approve_request(self.records.admin.pk, borrow_request.pk, "Enough units")

        borrow_request.refresh_from_db()
        self.assertEqual(borrow_request.status, RequestStatus.APPROVED)
        self.assertEqual(borrow_request.decided_by_id, self.records.admin.pk)
        self.assertEqual(borrow_request.decision_reason, "Enough units")
        self.assertEqual(
            UnitAllocation.objects.filter(request_item__request=borrow_request).count(), 2
        )
        self.assertEqual(self.unit_count(UnitStatus.RESERVED), 2)
        self.assertEqual(self.unit_count(UnitStatus.AVAILABLE), 1)
        self.assertTrue(
            AuditLog.objects.filter(
                action=AuditAction.REQUEST_APPROVED, target_id=borrow_request.pk
            ).exists()
        )

    def test_insufficient_units_reserve_nothing(self) -> None:
        make_units(self.item, 1)
        borrow_request = make_request(self.records.borrower, self.item, quantity=2)

        with self.assertRaises(WorkflowConflict) as context:
            approve_request(self.records.admin.pk, borrow_request.pk, "Try")

        self.assertIn("Nothing was reserved", str(context.exception))
        borrow_request.refresh_from_db()
        self.assertEqual(borrow_request.status, RequestStatus.PENDING)
        self.assertEqual(UnitAllocation.objects.count(), 0)
        self.assertEqual(self.unit_count(UnitStatus.AVAILABLE), 1)
        self.assertFalse(AuditLog.objects.filter(action=AuditAction.REQUEST_APPROVED).exists())

    def test_shortage_on_second_item_rolls_back_the_first(self) -> None:
        other = CatalogItem.objects.create(
            category=self.category, name="T13 Speaker", description="Speaker for T13 tests."
        )
        make_units(self.item, 2)
        borrow_request = make_request(self.records.borrower, self.item, quantity=1)
        RequestItem.objects.create(request=borrow_request, catalog_item=other, quantity=1)

        with self.assertRaises(WorkflowConflict):
            approve_request(self.records.admin.pk, borrow_request.pk, "Try")

        self.assertEqual(self.unit_count(UnitStatus.AVAILABLE), 2)
        self.assertEqual(UnitAllocation.objects.count(), 0)

    def test_requests_not_pending_cannot_be_decided(self) -> None:
        for status in (RequestStatus.CANCELLED, RequestStatus.REJECTED, RequestStatus.APPROVED):
            with self.subTest(status=status):
                borrow_request = make_request(self.records.borrower, self.item, status=status)
                with self.assertRaises(WorkflowConflict):
                    approve_request(self.records.admin.pk, borrow_request.pk, "Try")
                with self.assertRaises(WorkflowConflict):
                    reject_request(self.records.admin.pk, borrow_request.pk, "Try")

    def test_archived_item_blocks_approval(self) -> None:
        make_units(self.item, 1)
        borrow_request = make_request(self.records.borrower, self.item)
        CatalogItem.objects.filter(pk=self.item.pk).update(is_archived=True)

        with self.assertRaises(WorkflowConflict):
            approve_request(self.records.admin.pk, borrow_request.pk, "Try")

        self.assertEqual(self.unit_count(UnitStatus.AVAILABLE), 1)

    def test_archived_category_blocks_approval(self) -> None:
        make_units(self.item, 1)
        borrow_request = make_request(self.records.borrower, self.item)
        Category.objects.filter(pk=self.category.pk).update(is_archived=True)

        with self.assertRaises(WorkflowConflict):
            approve_request(self.records.admin.pk, borrow_request.pk, "Try")

        self.assertEqual(self.unit_count(UnitStatus.AVAILABLE), 1)

    def test_blank_reason_is_rejected(self) -> None:
        make_units(self.item, 1)
        borrow_request = make_request(self.records.borrower, self.item)
        for reason in ("", "   "):
            with self.subTest(reason=reason):
                with self.assertRaises(ValidationError):
                    approve_request(self.records.admin.pk, borrow_request.pk, reason)
                with self.assertRaises(ValidationError):
                    reject_request(self.records.admin.pk, borrow_request.pk, reason)
        borrow_request.refresh_from_db()
        self.assertEqual(borrow_request.status, RequestStatus.PENDING)

    def test_reject_records_reason_and_leaves_units_alone(self) -> None:
        make_units(self.item, 2)
        borrow_request = make_request(self.records.borrower, self.item)

        reject_request(self.records.admin.pk, borrow_request.pk, "Not for class use")

        borrow_request.refresh_from_db()
        self.assertEqual(borrow_request.status, RequestStatus.REJECTED)
        self.assertEqual(borrow_request.decision_reason, "Not for class use")
        self.assertEqual(UnitAllocation.objects.count(), 0)
        self.assertEqual(self.unit_count(UnitStatus.AVAILABLE), 2)
        self.assertTrue(
            AuditLog.objects.filter(
                action=AuditAction.REQUEST_REJECTED, target_id=borrow_request.pk
            ).exists()
        )

    def test_basic_user_cannot_decide(self) -> None:
        make_units(self.item, 1)
        borrow_request = make_request(self.records.borrower, self.item)

        with self.assertRaises(PermissionDenied):
            approve_request(self.records.borrower.pk, borrow_request.pk, "Self approval")

        borrow_request.refresh_from_db()
        self.assertEqual(borrow_request.status, RequestStatus.PENDING)

    def test_inactive_borrower_blocks_approval(self) -> None:
        make_units(self.item, 1)
        borrow_request = make_request(self.records.borrower, self.item)
        User.objects.filter(pk=self.records.borrower.pk).update(is_active=False)

        with self.assertRaises(WorkflowConflict):
            approve_request(self.records.admin.pk, borrow_request.pk, "Try")


class RequestDecisionViewTests(RequestTestBase):
    def approve_url(self, borrow_request: BorrowRequest) -> str:
        return reverse("borrowing_manage:request-approve", args=[borrow_request.pk])

    def test_get_shows_confirmation_and_changes_nothing(self) -> None:
        make_units(self.item, 1)
        borrow_request = make_request(self.records.borrower, self.item)
        self.client.force_login(self.records.admin)

        response = self.client.get(self.approve_url(borrow_request))

        self.assertEqual(response.status_code, 200)
        borrow_request.refresh_from_db()
        self.assertEqual(borrow_request.status, RequestStatus.PENDING)
        self.assertEqual(UnitAllocation.objects.count(), 0)

    def test_post_approves_and_redirects_to_detail(self) -> None:
        make_units(self.item, 1)
        borrow_request = make_request(self.records.borrower, self.item)
        self.client.force_login(self.records.admin)

        response = self.client.post(self.approve_url(borrow_request), {"reason": "Looks fine"})

        self.assertRedirects(
            response, reverse("borrowing_manage:request-detail", args=[borrow_request.pk])
        )
        borrow_request.refresh_from_db()
        self.assertEqual(borrow_request.status, RequestStatus.APPROVED)

    def test_insufficient_units_return_409_with_clear_message(self) -> None:
        make_units(self.item, 1)
        borrow_request = make_request(self.records.borrower, self.item, quantity=2)
        self.client.force_login(self.records.admin)

        response = self.client.post(self.approve_url(borrow_request), {"reason": "Try"})

        self.assertContains(response, "Nothing was reserved", status_code=409)
        self.assertEqual(UnitAllocation.objects.count(), 0)

    def test_blank_reason_shows_form_error_and_changes_nothing(self) -> None:
        make_units(self.item, 1)
        borrow_request = make_request(self.records.borrower, self.item)
        self.client.force_login(self.records.admin)

        response = self.client.post(self.approve_url(borrow_request), {"reason": ""})

        self.assertEqual(response.status_code, 200)
        borrow_request.refresh_from_db()
        self.assertEqual(borrow_request.status, RequestStatus.PENDING)

    def test_decided_request_says_it_can_no_longer_be_decided(self) -> None:
        borrow_request = make_request(
            self.records.borrower, self.item, status=RequestStatus.CANCELLED
        )
        self.client.force_login(self.records.admin)

        response = self.client.get(self.approve_url(borrow_request))

        self.assertContains(response, "can no longer be decided")

    def test_basic_user_receives_403(self) -> None:
        make_units(self.item, 1)
        borrow_request = make_request(self.records.borrower, self.item)
        self.client.force_login(self.records.borrower)

        self.assertEqual(self.client.get(self.approve_url(borrow_request)).status_code, 403)
        response = self.client.post(self.approve_url(borrow_request), {"reason": "Self approval"})
        self.assertEqual(response.status_code, 403)
        borrow_request.refresh_from_db()
        self.assertEqual(borrow_request.status, RequestStatus.PENDING)

    def test_anonymous_user_is_sent_to_login(self) -> None:
        borrow_request = make_request(self.records.borrower, self.item)
        url = self.approve_url(borrow_request)

        self.assertRedirects(self.client.get(url), f"{reverse('accounts:login')}?next={url}")

    def test_put_and_delete_are_405(self) -> None:
        borrow_request = make_request(self.records.borrower, self.item)
        self.client.force_login(self.records.admin)

        self.assertEqual(self.client.put(self.approve_url(borrow_request)).status_code, 405)
        self.assertEqual(self.client.delete(self.approve_url(borrow_request)).status_code, 405)

    def test_unknown_request_is_404(self) -> None:
        self.client.force_login(self.records.admin)

        response = self.client.get(reverse("borrowing_manage:request-approve", args=[999999]))

        self.assertEqual(response.status_code, 404)


class RequestQueueAndDetailTests(RequestTestBase):
    def test_queue_lists_newest_first(self) -> None:
        first = make_request(self.records.borrower, self.item)
        second = make_request(self.records.borrower, self.item)
        self.client.force_login(self.records.admin)

        response = self.client.get(reverse("borrowing_manage:request-list"))

        self.assertEqual([r.pk for r in response.context["page"]], [second.pk, first.pk])

    def test_status_filter_and_search(self) -> None:
        pending = make_request(self.records.borrower, self.item)
        make_request(self.records.borrower, self.item, status=RequestStatus.CANCELLED)
        self.client.force_login(self.records.admin)
        url = reverse("borrowing_manage:request-list")

        by_status = self.client.get(url, {"status": RequestStatus.PENDING})
        by_id = self.client.get(url, {"q": str(pending.pk)})
        by_name = self.client.get(url, {"q": self.records.borrower.username})

        self.assertEqual([r.pk for r in by_status.context["page"]], [pending.pk])
        self.assertEqual([r.pk for r in by_id.context["page"]], [pending.pk])
        self.assertEqual(len(by_name.context["page"]), 2)

    def test_unicode_numeric_search_matches_username_and_decimal_request_id(self) -> None:
        borrow_request: BorrowRequest = make_request(
            self.records.borrower, self.item, 1, RequestStatus.PENDING
        )
        User.objects.filter(pk=self.records.borrower.pk).update(username="borrower²")
        self.client.force_login(self.records.admin)
        url: str = reverse("borrowing_manage:request-list")

        by_username = self.client.get(url, {"q": "²"})
        decimal_id: str = str(borrow_request.pk).translate(
            str.maketrans("0123456789", "٠١٢٣٤٥٦٧٨٩")
        )
        by_id = self.client.get(url, {"q": decimal_id})

        self.assertEqual(by_username.status_code, 200)
        self.assertEqual([row.pk for row in by_username.context["page"]], [borrow_request.pk])
        self.assertEqual(by_id.status_code, 200)
        self.assertEqual([row.pk for row in by_id.context["page"]], [borrow_request.pk])

    def test_reversed_date_range_shows_error(self) -> None:
        make_request(self.records.borrower, self.item)
        self.client.force_login(self.records.admin)

        response = self.client.get(
            reverse("borrowing_manage:request-list"),
            {"date_from": "2026-10-20", "date_to": "2026-10-01"},
        )

        self.assertContains(response, "Correct the filters")
        self.assertEqual(len(response.context["page"]), 0)

    def test_bad_page_numbers_are_404(self) -> None:
        self.client.force_login(self.records.admin)
        url = reverse("borrowing_manage:request-list")

        self.assertEqual(self.client.get(url, {"page": "99"}).status_code, 404)
        self.assertEqual(self.client.get(url, {"page": "abc"}).status_code, 404)

    def test_basic_user_cannot_open_queue_or_detail(self) -> None:
        borrow_request = make_request(self.records.borrower, self.item)
        self.client.force_login(self.records.borrower)

        self.assertEqual(self.client.get(reverse("borrowing_manage:request-list")).status_code, 403)
        detail = reverse("borrowing_manage:request-detail", args=[borrow_request.pk])
        self.assertEqual(self.client.get(detail).status_code, 403)

    def test_detail_shows_availability_before_and_reserved_units_after_approval(self) -> None:
        make_units(self.item, 3)
        borrow_request = make_request(self.records.borrower, self.item)
        self.client.force_login(self.records.admin)
        url = reverse("borrowing_manage:request-detail", args=[borrow_request.pk])

        before = self.client.get(url).context["lines"][0]
        approve_request(self.records.admin.pk, borrow_request.pk, "Go ahead")
        after = self.client.get(url).context["lines"][0]

        self.assertEqual(before["available"], 3)
        self.assertEqual(before["units"], [])
        self.assertEqual(after["available"], 2)
        self.assertEqual(len(after["units"]), 1)

    def test_cancelled_reservation_is_hidden_without_deleting_allocation_history(self) -> None:
        unit: EquipmentUnit = make_units(self.item, 1)[0]
        borrow_request: BorrowRequest = make_request(
            self.records.borrower, self.item, 1, RequestStatus.PENDING
        )
        self.client.force_login(self.records.admin)
        approval = self.client.post(
            reverse("borrowing_manage:request-approve", args=[borrow_request.pk]),
            {"reason": "Approve before borrower cancellation"},
        )
        self.assertEqual(approval.status_code, 302)

        self.client.force_login(self.records.borrower)
        cancellation = self.client.post(reverse("portal:request-cancel", args=[borrow_request.pk]))
        self.assertEqual(cancellation.status_code, 302)

        self.client.force_login(self.records.admin)
        response = self.client.get(
            reverse("borrowing_manage:request-detail", args=[borrow_request.pk])
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["lines"][0]["units"], [])
        self.assertEqual(response.context["lines"][0]["available"], 1)
        self.assertNotContains(response, unit.asset_code)
        unit.refresh_from_db()
        borrow_request.refresh_from_db()
        allocation: UnitAllocation = UnitAllocation.objects.get(
            request_item__request=borrow_request, unit=unit
        )
        self.assertEqual(unit.status, UnitStatus.AVAILABLE)
        self.assertEqual(borrow_request.status, RequestStatus.CANCELLED)
        self.assertIsNotNone(allocation.cancelled_at)
        self.assertEqual(allocation.ended_at, allocation.cancelled_at)
        self.assertTrue(
            AuditLog.objects.filter(
                action=AuditAction.REQUEST_CANCELLED, target_id=borrow_request.pk
            ).exists()
        )

    def test_unknown_detail_is_404(self) -> None:
        self.client.force_login(self.records.admin)

        response = self.client.get(reverse("borrowing_manage:request-detail", args=[999999]))

        self.assertEqual(response.status_code, 404)
