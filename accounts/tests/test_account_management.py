"""T05 account-management authorization, history, and transaction checks."""

from django.contrib.auth import SESSION_KEY
from django.core.exceptions import PermissionDenied
from django.db import IntegrityError, connection
from django.test import Client, TestCase
from django.urls import reverse

from accounts.models import Profile, User, UserRole
from accounts.services import (
    AccountStatusConflict,
    activate_basic_user,
    deactivate_basic_user,
)
from borrowing.models import BorrowRequest, Loan, RequestStatus, UnitAllocation
from operations.models import AuditAction, AuditLog, AuditTarget
from operations.tests.records import IssuedRecords, create_issued_records


def create_account(username: str, role: UserRole, is_active: bool) -> User:
    """Create a fictional account with the Profile required by the product contract."""
    user: User = User.objects.create_user(
        username=username,
        password=None,
        first_name="Fictional",
        last_name="Account",
        email=f"{username}@example.invalid",
        role=role,
        is_active=is_active,
    )
    Profile.objects.create(user=user, contact_number="")
    return user


class AccountManagementRouteTests(TestCase):
    records: IssuedRecords

    @classmethod
    def setUpTestData(cls) -> None:
        cls.records = create_issued_records()
        cls.admin: User = cls.records.catalog.admin
        cls.borrower: User = cls.records.catalog.borrower
        cls.inactive: User = create_account("inactive_basic", UserRole.BASIC_USER, False)
        cls.other_admin: User = create_account("other_admin", UserRole.ADMIN, True)
        Profile.objects.filter(user=cls.borrower).update(contact_number="555-0100")
        for index in range(26):
            create_account(f"page_user_{index:02d}", UserRole.BASIC_USER, True)

    def setUp(self) -> None:
        self.client.force_login(self.admin)

    def test_admin_can_search_filter_and_paginate_only_basic_users(self) -> None:
        list_url: str = reverse("accounts:manage-list")
        response = self.client.get(list_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.borrower.username)
        self.assertNotContains(response, self.admin.username)
        self.assertEqual(len(response.context["page"].object_list), 25)

        contact_response = self.client.get(list_url, {"q": "555-0100"})
        self.assertContains(contact_response, self.borrower.username)
        self.assertNotContains(contact_response, self.inactive.username)
        trimmed_response = self.client.get(list_url, {"q": f"  {self.borrower.username}  "})
        self.assertContains(trimmed_response, self.borrower.username)

        inactive_response = self.client.get(list_url, {"active": "false"})
        self.assertContains(inactive_response, self.inactive.username)
        self.assertNotContains(inactive_response, self.borrower.username)

        second_page = self.client.get(list_url, {"page": "2"})
        self.assertEqual(second_page.status_code, 200)
        self.assertEqual(second_page.context["page"].number, 2)
        self.assertEqual(self.client.get(list_url, {"page": "not-a-page"}).status_code, 404)
        self.assertEqual(self.client.get(list_url, {"page": "99"}).status_code, 404)

    def test_search_and_status_values_remain_visible_through_pagination(self) -> None:
        list_url: str = reverse("accounts:manage-list")
        first_page = self.client.get(
            list_url,
            {"q": "page_user", "active": "true", "page": "1"},
        )
        self.assertEqual(first_page.status_code, 200)
        self.assertContains(first_page, 'name="q" value="page_user"')
        self.assertContains(
            first_page,
            '<option value="true" selected>Active</option>',
            html=True,
        )
        self.assertContains(first_page, "?q=page_user&amp;active=true&amp;page=2")

        second_page = self.client.get(
            list_url,
            {"q": "page_user", "active": "true", "page": "2"},
        )
        self.assertEqual(second_page.status_code, 200)
        self.assertContains(second_page, 'name="q" value="page_user"')
        self.assertContains(
            second_page,
            '<option value="true" selected>Active</option>',
            html=True,
        )

    def test_invalid_search_filters_render_errors_without_broadening_results(self) -> None:
        list_url: str = reverse("accounts:manage-list")
        long_query_response = self.client.get(list_url, {"q": "x" * 201})
        self.assertEqual(long_query_response.status_code, 200)
        self.assertContains(long_query_response, "Ensure this value has at most 200 characters")
        self.assertEqual(len(long_query_response.context["page"].object_list), 0)

        invalid_status_response = self.client.get(list_url, {"active": "yes"})
        self.assertEqual(invalid_status_response.status_code, 200)
        self.assertContains(invalid_status_response, "Select a valid choice")
        self.assertEqual(len(invalid_status_response.context["page"].object_list), 0)

    def test_detail_shows_profile_requests_and_borrowing_history(self) -> None:
        response = self.client.get(reverse("accounts:manage-detail", args=[self.borrower.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.borrower.username)
        self.assertContains(response, "555-0100")
        self.assertContains(response, self.records.request.purpose)
        self.assertContains(response, self.records.catalog.item.name)
        self.assertContains(response, f"#{self.records.loan.pk}")
        self.assertContains(response, self.records.catalog.unit.asset_code)

    def test_anonymous_and_basic_users_cannot_reach_any_management_route(self) -> None:
        urls: tuple[str, ...] = (
            reverse("accounts:manage-list"),
            reverse("accounts:manage-detail", args=[self.borrower.pk]),
            reverse("accounts:manage-activate", args=[self.inactive.pk]),
            reverse("accounts:manage-deactivate", args=[self.borrower.pk]),
        )
        anonymous_client = Client()
        for url in urls:
            with self.subTest(actor="anonymous", url=url):
                response = anonymous_client.get(url)
                self.assertEqual(response.status_code, 302)
                self.assertIn(reverse("accounts:login"), response.headers["Location"])

        basic_client = Client()
        basic_client.force_login(self.borrower)
        for url in urls:
            with self.subTest(actor="basic", url=url):
                self.assertEqual(basic_client.get(url).status_code, 403)
        self.assertEqual(
            basic_client.post(
                reverse("accounts:manage-deactivate", args=[self.inactive.pk])
            ).status_code,
            403,
        )

    def test_admin_targets_are_hidden_from_detail_and_both_actions(self) -> None:
        urls: tuple[str, ...] = (
            reverse("accounts:manage-detail", args=[self.other_admin.pk]),
            reverse("accounts:manage-activate", args=[self.other_admin.pk]),
            reverse("accounts:manage-deactivate", args=[self.other_admin.pk]),
        )
        for url in urls:
            with self.subTest(method="GET", url=url):
                self.assertEqual(self.client.get(url).status_code, 404)
            if url != urls[0]:
                with self.subTest(method="POST", url=url):
                    self.assertEqual(self.client.post(url).status_code, 404)
        self.other_admin.refresh_from_db()
        self.assertTrue(self.other_admin.is_active)
        self.assertEqual(self.other_admin.role, UserRole.ADMIN)

    def test_forged_fields_cannot_change_roles_flags_or_another_target(self) -> None:
        response = self.client.post(
            reverse("accounts:manage-deactivate", args=[self.borrower.pk]),
            {
                "role": UserRole.ADMIN,
                "is_staff": "true",
                "is_superuser": "true",
                "target_id": self.other_admin.pk,
                "actor_id": self.other_admin.pk,
                "username": "forged_username",
                "email": "forged@example.invalid",
                "password": "forged-password",
            },
        )
        self.assertRedirects(
            response,
            reverse("accounts:manage-detail", args=[self.borrower.pk]),
            fetch_redirect_response=False,
        )
        self.borrower.refresh_from_db()
        self.other_admin.refresh_from_db()
        self.assertFalse(self.borrower.is_active)
        self.assertEqual(self.borrower.username, "fictional_borrower")
        self.assertEqual(self.borrower.email, "borrower@example.invalid")
        self.assertEqual(self.borrower.role, UserRole.BASIC_USER)
        self.assertFalse(self.borrower.is_staff)
        self.assertFalse(self.borrower.is_superuser)
        self.assertTrue(self.other_admin.is_active)

    def test_activate_deactivate_audit_and_repeated_action_protocol(self) -> None:
        deactivate_url: str = reverse("accounts:manage-deactivate", args=[self.borrower.pk])
        self.assertEqual(self.client.get(deactivate_url).status_code, 200)
        self.borrower.refresh_from_db()
        self.assertTrue(self.borrower.is_active)

        deactivate_response = self.client.post(deactivate_url)
        self.assertEqual(deactivate_response.status_code, 302)
        repeated_deactivate = self.client.post(deactivate_url)
        self.assertEqual(repeated_deactivate.status_code, 409)
        deactivate_audit: AuditLog = AuditLog.objects.get(
            action=AuditAction.ACCOUNT_DEACTIVATED, target_id=self.borrower.pk
        )
        self.assertEqual(
            (deactivate_audit.actor_id, deactivate_audit.target_model),
            (self.admin.pk, AuditTarget.USER),
        )
        self.assertEqual(
            AuditLog.objects.filter(
                action=AuditAction.ACCOUNT_DEACTIVATED, target_id=self.borrower.pk
            ).count(),
            1,
        )

        activate_url: str = reverse("accounts:manage-activate", args=[self.borrower.pk])
        activate_response = self.client.post(activate_url)
        self.assertEqual(activate_response.status_code, 302)
        repeated_activate = self.client.post(activate_url)
        self.assertEqual(repeated_activate.status_code, 409)
        activate_audit: AuditLog = AuditLog.objects.get(
            action=AuditAction.ACCOUNT_ACTIVATED, target_id=self.borrower.pk
        )
        self.assertEqual(
            (activate_audit.actor_id, activate_audit.target_model),
            (self.admin.pk, AuditTarget.USER),
        )

    def test_status_actions_require_post_and_csrf_for_mutation(self) -> None:
        deactivate_url: str = reverse("accounts:manage-deactivate", args=[self.borrower.pk])
        self.assertEqual(self.client.put(deactivate_url).status_code, 405)

        csrf_client = Client(enforce_csrf_checks=True)
        csrf_client.force_login(self.admin)
        confirmation = csrf_client.get(deactivate_url)
        self.assertEqual(confirmation.status_code, 200)
        self.assertEqual(csrf_client.post(deactivate_url).status_code, 403)
        csrf_token: str = csrf_client.cookies["csrftoken"].value
        response = csrf_client.post(deactivate_url, HTTP_X_CSRFTOKEN=csrf_token)
        self.assertEqual(response.status_code, 302)

    def test_deactivated_user_session_is_denied_by_shared_middleware(self) -> None:
        borrower_client = Client()
        borrower_client.force_login(self.borrower)
        self.assertEqual(borrower_client.get(reverse("portal:home")).status_code, 200)

        response = self.client.post(reverse("accounts:manage-deactivate", args=[self.borrower.pk]))
        self.assertEqual(response.status_code, 302)
        denied_response = borrower_client.get(reverse("portal:home"))
        self.assertEqual(denied_response.status_code, 403)
        self.assertNotIn(SESSION_KEY, borrower_client.session)

    def test_deactivation_preserves_account_profile_and_transaction_history(self) -> None:
        preserved_counts: tuple[int, int, int] = (
            BorrowRequest.objects.filter(owner=self.borrower).count(),
            Loan.objects.filter(request__owner=self.borrower).count(),
            UnitAllocation.objects.filter(request_item__request__owner=self.borrower).count(),
        )
        response = self.client.post(reverse("accounts:manage-deactivate", args=[self.borrower.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(pk=self.borrower.pk).exists())
        self.assertTrue(Profile.objects.filter(user=self.borrower).exists())
        self.assertEqual(
            (
                BorrowRequest.objects.filter(owner=self.borrower).count(),
                Loan.objects.filter(request__owner=self.borrower).count(),
                UnitAllocation.objects.filter(request_item__request__owner=self.borrower).count(),
            ),
            preserved_counts,
        )
        self.records.request.refresh_from_db()
        self.records.loan.refresh_from_db()
        self.assertEqual(self.records.request.status, RequestStatus.ISSUED)
        self.assertIsNone(self.records.loan.closed_at)


class AccountStatusServiceTests(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.admin: User = create_account("service_admin", UserRole.ADMIN, True)
        cls.other_admin: User = create_account("service_other_admin", UserRole.ADMIN, True)
        cls.inactive_admin: User = create_account("service_inactive_admin", UserRole.ADMIN, False)
        cls.borrower: User = create_account("service_basic", UserRole.BASIC_USER, True)

    def test_service_rechecks_actor_role_target_role_and_current_state(self) -> None:
        with self.assertRaises(PermissionDenied):
            deactivate_basic_user(self.borrower.pk, self.borrower.pk)
        with self.assertRaises(User.DoesNotExist):
            deactivate_basic_user(self.admin.pk, self.other_admin.pk)
        with self.assertRaises(PermissionDenied):
            deactivate_basic_user(self.inactive_admin.pk, self.borrower.pk)
        self.other_admin.refresh_from_db()
        self.assertTrue(self.other_admin.is_active)
        self.assertFalse(
            AuditLog.objects.filter(
                action__in=(
                    AuditAction.ACCOUNT_ACTIVATED,
                    AuditAction.ACCOUNT_DEACTIVATED,
                )
            ).exists()
        )

        deactivate_basic_user(self.admin.pk, self.borrower.pk)
        with self.assertRaises(AccountStatusConflict):
            deactivate_basic_user(self.admin.pk, self.borrower.pk)
        activate_basic_user(self.admin.pk, self.borrower.pk)

    def test_database_audit_failure_rolls_back_account_status(self) -> None:
        with connection.cursor() as cursor:
            cursor.execute(
                "ALTER TABLE operations_auditlog "
                "ADD CONSTRAINT test_reject_account_deactivation "
                "CHECK (action <> 'ACCOUNT_DEACTIVATED')"
            )
        with self.assertRaises(IntegrityError):
            deactivate_basic_user(self.admin.pk, self.borrower.pk)
        self.borrower.refresh_from_db()
        self.assertTrue(self.borrower.is_active)
        self.assertFalse(
            AuditLog.objects.filter(
                action=AuditAction.ACCOUNT_DEACTIVATED,
                target_id=self.borrower.pk,
            ).exists()
        )
