"""Tests for T15: due date revisions, loan issuance, loan detail, and borrowing slips."""

from datetime import timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from borrowing.models import BorrowRequest, LoanUnit, RequestItem, RequestStatus
from borrowing.services import (
    WorkflowConflict,
    approve_request,
    issue_request,
    revise_due_date,
)
from inventory.models import UnitStatus
from operations.tests.records import CatalogRecords, create_catalog_records


class LoanIssueWorkflowTests(TestCase):
    def setUp(self) -> None:
        self.catalog: CatalogRecords = create_catalog_records()
        self.admin = self.catalog.admin
        self.borrower = self.catalog.borrower
        self.unit1 = self.catalog.unit
        self.today = timezone.localdate()
        self.initial_due = self.today + timedelta(days=3)

        self.borrow_request = BorrowRequest.objects.create(
            owner=self.borrower,
            purpose="T15 Lab Experiment",
            submitted_at=timezone.now(),
            submitted_on=self.today,
            desired_due_date=self.initial_due,
            agreed_due_date=self.initial_due,
            max_loan_days_applied=7,
            max_quantity_applied=3,
            status=RequestStatus.PENDING,
        )
        RequestItem.objects.create(
            request=self.borrow_request,
            catalog_item=self.catalog.item,
            quantity=1,
        )

    def test_revise_due_date_on_approved_request(self) -> None:
        approve_request(
            actor_id=self.admin.pk,
            request_id=self.borrow_request.pk,
            reason="Approved for class demonstration",
        )
        self.borrow_request.refresh_from_db()

        new_due = self.today + timedelta(days=5)
        revise_due_date(
            actor_id=self.admin.pk,
            request_id=self.borrow_request.pk,
            agreed_due_date=new_due,
            reason="Instructor requested extension before pickup",
        )
        self.borrow_request.refresh_from_db()
        self.assertEqual(self.borrow_request.agreed_due_date, new_due)

    def test_revise_due_date_fails_on_non_approved_request(self) -> None:
        new_due = self.today + timedelta(days=5)
        with self.assertRaises(WorkflowConflict):
            revise_due_date(
                actor_id=self.admin.pk,
                request_id=self.borrow_request.pk,
                agreed_due_date=new_due,
                reason="Premature extension attempt",
            )

    def test_issue_request_transitions_units_and_creates_loan(self) -> None:
        approve_request(
            actor_id=self.admin.pk,
            request_id=self.borrow_request.pk,
            reason="Approved for class demonstration",
        )
        self.unit1.refresh_from_db()
        self.assertEqual(self.unit1.status, UnitStatus.RESERVED)

        loan = issue_request(actor_id=self.admin.pk, request_id=self.borrow_request.pk)

        self.borrow_request.refresh_from_db()
        self.assertEqual(self.borrow_request.status, RequestStatus.ISSUED)
        self.assertEqual(loan.request, self.borrow_request)
        self.assertEqual(loan.issued_by, self.admin)

        self.unit1.refresh_from_db()
        self.assertEqual(self.unit1.status, UnitStatus.ISSUED)
        self.assertEqual(LoanUnit.objects.filter(loan=loan).count(), 1)

    def test_issue_request_conflict_if_already_issued(self) -> None:
        approve_request(
            actor_id=self.admin.pk,
            request_id=self.borrow_request.pk,
            reason="Approved for class demonstration",
        )
        issue_request(actor_id=self.admin.pk, request_id=self.borrow_request.pk)

        with self.assertRaises(WorkflowConflict):
            issue_request(actor_id=self.admin.pk, request_id=self.borrow_request.pk)

    def test_manage_loan_views_render_for_admin(self) -> None:
        self.client.force_login(self.admin)
        approve_request(
            actor_id=self.admin.pk,
            request_id=self.borrow_request.pk,
            reason="Approved for class demonstration",
        )
        loan = issue_request(actor_id=self.admin.pk, request_id=self.borrow_request.pk)

        list_resp = self.client.get(reverse("borrowing_manage:loan-list"))
        self.assertEqual(list_resp.status_code, 200)
        self.assertContains(list_resp, f"#{loan.pk}")

        filter_resp = self.client.get(
            reverse("borrowing_manage:loan-list"), {"q": self.borrower.username}
        )
        self.assertEqual(filter_resp.status_code, 200)
        self.assertContains(filter_resp, f"#{loan.pk}")

        detail_resp = self.client.get(
            reverse("borrowing_manage:loan-detail", kwargs={"loan_id": loan.pk})
        )
        self.assertEqual(detail_resp.status_code, 200)
        self.assertContains(detail_resp, self.unit1.asset_code)

        slip_resp = self.client.get(
            reverse("borrowing_manage:loan-slip", kwargs={"loan_id": loan.pk})
        )
        self.assertEqual(slip_resp.status_code, 200)
        self.assertContains(slip_resp, self.unit1.asset_code)
        self.assertContains(slip_resp, "Equipment Borrowing Slip")

    def test_loan_list_filters_by_status(self) -> None:
        self.client.force_login(self.admin)
        approve_request(
            actor_id=self.admin.pk,
            request_id=self.borrow_request.pk,
            reason="Approved for class demonstration",
        )
        loan = issue_request(actor_id=self.admin.pk, request_id=self.borrow_request.pk)

        active_resp = self.client.get(
            reverse("borrowing_manage:loan-list"), {"status": "active"}
        )
        self.assertEqual(active_resp.status_code, 200)
        self.assertContains(active_resp, f"#{loan.pk}")

        closed_resp = self.client.get(
            reverse("borrowing_manage:loan-list"), {"status": "closed"}
        )
        self.assertEqual(closed_resp.status_code, 200)
        self.assertNotContains(closed_resp, f"#{loan.pk}")