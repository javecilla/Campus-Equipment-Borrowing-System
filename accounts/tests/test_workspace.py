"""T20 owner summaries and integration across existing request/return workflows."""

from datetime import timedelta

from django.contrib.auth import SESSION_KEY
from django.db import connection
from django.test import Client, TestCase
from django.test.utils import CaptureQueriesContext
from django.urls import reverse
from django.utils import timezone

from accounts.models import Profile, User, UserRole
from borrowing.models import BorrowRequest, RequestStatus
from borrowing.queries import borrower_workspace
from borrowing.release_services import release_request
from borrowing.return_services import ReturnInput, return_units
from borrowing.services import approve_request, submit_request
from inventory.models import EquipmentUnit, UnitCondition, UnitStatus
from operations.models import AuditLog
from operations.tests.records import create_catalog_records, create_request
from operations.validation import RequestedItem


class BorrowerWorkspaceTests(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.records = create_catalog_records()
        cls.other = User.objects.create_user(
            username="t20_other", password=None, role=UserRole.BASIC_USER
        )
        Profile.objects.create(user=cls.other, contact_number="")

    def test_empty_home_has_real_destinations_without_writing_history(self) -> None:
        self.client.force_login(self.records.borrower)
        before = AuditLog.objects.count()
        with CaptureQueriesContext(connection) as queries:
            response = self.client.get(reverse("portal:home"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/portal/home.html")
        self.assertContains(response, 'data-testid="home-loans-empty"')
        self.assertContains(response, 'data-testid="home-requests-empty"')
        self.assertEqual(response.context["workspace"].active_loans, 0)
        for name in ("equipment-list", "request-create", "request-list", "loan-list", "profile"):
            self.assertContains(response, reverse(f"portal:{name}"))
        self.assertEqual(AuditLog.objects.count(), before)
        self.assertFalse(BorrowRequest.objects.exists())
        self.assertFalse(
            any(q["sql"].lstrip().split()[0] in {"INSERT", "UPDATE", "DELETE"} for q in queries)
        )

    def test_summary_ignores_supplied_owner_and_excludes_another_borrower(self) -> None:
        own = create_request(self.records.borrower.pk, self.records.item.pk, timezone.now())
        foreign = create_request(self.other.pk, self.records.item.pk, timezone.now())
        BorrowRequest.objects.filter(pk=foreign.request_id).update(purpose="T20 private purpose")
        self.client.force_login(self.records.borrower)
        response = self.client.get(
            reverse("portal:home"), {"owner_id": self.other.pk, "user_id": self.other.pk}
        )
        workspace = response.context["workspace"]
        self.assertEqual(workspace.pending_requests, 1)
        self.assertEqual([r.pk for r in workspace.recent_requests], [own.request_id])
        self.assertNotContains(response, "T20 private purpose")
        self.assertNotContains(
            response, reverse("portal:request-detail", args=[foreign.request_id])
        )
        self.assertEqual(
            self.client.get(
                reverse("portal:request-detail", args=[foreign.request_id])
            ).status_code,
            404,
        )

    def test_home_enforces_active_borrower_and_safe_methods(self) -> None:
        url = reverse("portal:home")
        self.assertEqual(self.client.get(url).status_code, 302)
        self.client.force_login(self.records.admin)
        self.assertEqual(self.client.get(url).status_code, 403)
        self.client.force_login(self.records.borrower)
        self.assertEqual(self.client.head(url).status_code, 200)
        self.assertEqual(self.client.post(url).status_code, 405)
        User.objects.filter(pk=self.records.borrower.pk).update(is_active=False)
        self.assertEqual(self.client.get(url).status_code, 403)
        self.assertNotIn(SESSION_KEY, self.client.session)

    def test_summary_follows_approval_release_partial_and_final_return(self) -> None:
        EquipmentUnit.objects.create(
            catalog_item=self.records.item,
            asset_code="T20-CAM-002",
            condition=UnitCondition.GOOD,
            acquired_on=timezone.localdate(),
            status=UnitStatus.AVAILABLE,
        )
        request = submit_request(
            self.records.borrower.pk,
            "T20 fictional workshop",
            timezone.localdate() + timedelta(days=2),
            (RequestedItem(self.records.item.pk, 2),),
        )
        self.client.force_login(self.records.borrower)
        url = reverse("portal:home")
        self.assertEqual(self.client.get(url).context["workspace"].pending_requests, 1)
        approve_request(self.records.admin.pk, request.pk, "T20 fictional approval")
        approved = self.client.get(url).context["workspace"]
        self.assertEqual((approved.pending_requests, approved.approved_requests), (0, 1))
        loan = release_request(self.records.admin.pk, request.pk)
        issued = self.client.get(url).context["workspace"]
        self.assertEqual((issued.approved_requests, issued.active_loans), (0, 1))
        first, second = tuple(loan.units.order_by("pk"))
        return_units(
            self.records.admin.pk, loan.pk, (ReturnInput(first.pk, UnitCondition.GOOD, "", ""),)
        )
        partial = self.client.get(url).context["workspace"]
        self.assertEqual(partial.active_loans, 1)
        self.assertEqual(partial.due_loans[0].outstanding_quantity, 1)
        return_units(
            self.records.admin.pk,
            loan.pk,
            (ReturnInput(second.pk, UnitCondition.DAMAGED, "", "T20 fictional lens damage"),),
        )
        final = self.client.get(url).context["workspace"]
        self.assertEqual((final.active_loans, final.overdue_loans), (0, 0))
        self.assertEqual(final.due_loans, ())
        self.assertEqual(final.recent_requests[0].status, RequestStatus.RETURNED)

    def test_due_today_boundary_foreign_loans_and_bounded_previews(self) -> None:
        today = timezone.localdate()
        own_loans = []
        for index in range(7):
            EquipmentUnit.objects.create(
                catalog_item=self.records.item,
                asset_code=f"T20-PREVIEW-{index}",
                condition=UnitCondition.GOOD,
                acquired_on=today,
                status=UnitStatus.AVAILABLE,
            )
            line = create_request(self.records.borrower.pk, self.records.item.pk, timezone.now())
            approve_request(self.records.admin.pk, line.request_id, "T20 preview approval")
            own_loans.append(release_request(self.records.admin.pk, line.request_id))
        foreign = create_request(self.other.pk, self.records.item.pk, timezone.now())
        approve_request(self.records.admin.pk, foreign.request_id, "T20 foreign approval")
        release_request(self.records.admin.pk, foreign.request_id)
        due_date = own_loans[0].due_date
        workspace = borrower_workspace(self.records.borrower.pk, due_date)
        self.assertEqual((workspace.active_loans, workspace.overdue_loans), (7, 0))
        self.assertEqual(len(workspace.recent_requests), 5)
        self.assertEqual(
            [r.pk for r in workspace.recent_requests],
            sorted([loan.request_id for loan in own_loans], reverse=True)[:5],
        )
        self.assertEqual(
            [loan.pk for loan in workspace.due_loans], [loan.pk for loan in own_loans[:5]]
        )
        self.assertEqual(
            borrower_workspace(
                self.records.borrower.pk, due_date + timedelta(days=1)
            ).overdue_loans,
            7,
        )

    def test_shared_pagination_keeps_status_and_invalid_filter_has_recovery(self) -> None:
        for _ in range(8):
            create_request(self.records.borrower.pk, self.records.item.pk, timezone.now())
        self.client.force_login(self.records.borrower)
        first = self.client.get(reverse("portal:request-list"), {"status": "PENDING"})
        self.assertContains(first, 'href="?status=PENDING&amp;page=2"')
        self.assertContains(first, 'data-testid="pagination-next"')
        second = self.client.get(reverse("portal:request-list"), {"status": "PENDING", "page": 2})
        self.assertEqual(len(second.context["page"]), 2)
        self.assertContains(second, 'data-testid="pagination-prev"')
        invalid = self.client.get(reverse("portal:request-list"), {"status": "INVALID"})
        self.assertContains(invalid, 'data-testid="request-invalid-filters"')
        self.assertNotContains(invalid, 'data-testid="request-empty-state"')

    def test_confirmation_is_read_only_and_post_message_uses_shared_live_region(self) -> None:
        line = create_request(self.records.borrower.pk, self.records.item.pk, timezone.now())
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.records.borrower)
        cancel_url = reverse("portal:request-cancel", args=[line.request_id])
        confirmation = client.get(cancel_url)
        self.assertContains(confirmation, 'data-testid="request-cancel-keep"')
        self.assertEqual(
            BorrowRequest.objects.get(pk=line.request_id).status, RequestStatus.PENDING
        )
        self.assertEqual(client.post(cancel_url).status_code, 403)
        result = client.post(
            cancel_url, HTTP_X_CSRFTOKEN=client.cookies["csrftoken"].value, follow=True
        )
        self.assertContains(result, 'data-testid="workspace-message"')
        self.assertContains(result, 'role="status"')
        self.assertEqual(result.context["borrow_request"].status, RequestStatus.CANCELLED)
