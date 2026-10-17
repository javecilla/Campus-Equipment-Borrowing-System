"""Observable T04 login, role, active-session, ownership, and command checks."""

from datetime import timedelta
from io import StringIO
from typing import cast
from unittest.mock import patch

from django.contrib.auth import SESSION_KEY
from django.core.management import call_command
from django.core.management.base import CommandError
from django.http import HttpRequest, HttpResponse
from django.test import Client, TestCase, override_settings
from django.urls import URLPattern, path, reverse
from django.utils import timezone

from accounts.access import basic_user_required, get_owned_object_or_404
from accounts.models import Profile, User, UserRole
from borrowing.models import BorrowRequest, RequestStatus

PASSWORD = "Correct-Horse-Battery-Staple-2026!"


def create_account(username: str, role: UserRole, is_active: bool) -> User:
    user: User = User.objects.create_user(
        username=username,
        password=PASSWORD,
        first_name="Fictional",
        last_name="Account",
        email=f"{username}@example.invalid",
        role=role,
        is_active=is_active,
    )
    Profile.objects.create(user=user, contact_number="")
    return user


@basic_user_required
def owned_request_probe(request: HttpRequest, object_id: int) -> HttpResponse:
    record: BorrowRequest = get_owned_object_or_404(
        BorrowRequest.objects.all(),
        cast(User, request.user),
        object_id,
        "owner_id",
    )
    return HttpResponse(str(record.pk))


urlpatterns: list[URLPattern] = [
    path("owned-requests/<int:object_id>/", owned_request_probe, name="owned-request-probe"),
]


class AuthenticationRouteTests(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.admin: User = create_account("admin_user", UserRole.ADMIN, True)
        cls.borrower: User = create_account("basic_user", UserRole.BASIC_USER, True)
        cls.inactive: User = create_account("inactive_user", UserRole.BASIC_USER, False)

    def test_login_redirects_from_stored_role_and_ignores_forged_role(self) -> None:
        basic_client = Client()
        basic_response = basic_client.post(
            reverse("accounts:login"),
            {"username": self.borrower.username, "password": PASSWORD, "role": UserRole.ADMIN},
        )
        self.assertRedirects(basic_response, reverse("portal:home"), fetch_redirect_response=False)

        admin_client = Client()
        admin_response = admin_client.post(
            reverse("accounts:login"),
            {"username": self.admin.username, "password": PASSWORD, "role": UserRole.BASIC_USER},
        )
        self.assertRedirects(
            admin_response, reverse("operations:dashboard"), fetch_redirect_response=False
        )

    def test_login_accepts_only_same_role_next_paths(self) -> None:
        wrong_role_response = self.client.post(
            f"{reverse('accounts:login')}?next=/manage/",
            {
                "username": self.borrower.username,
                "password": PASSWORD,
                "next": "/manage/",
            },
        )
        self.assertRedirects(
            wrong_role_response, reverse("portal:home"), fetch_redirect_response=False
        )

        self.client.logout()
        unsafe_response = self.client.post(
            reverse("accounts:login"),
            {
                "username": self.borrower.username,
                "password": PASSWORD,
                "next": "https://example.invalid/portal/",
            },
        )
        self.assertRedirects(unsafe_response, reverse("portal:home"), fetch_redirect_response=False)

        self.client.logout()
        safe_response = self.client.post(
            reverse("accounts:login"),
            {
                "username": self.borrower.username,
                "password": PASSWORD,
                "next": "/portal/?from=login",
            },
        )
        self.assertRedirects(safe_response, "/portal/?from=login", fetch_redirect_response=False)

    def test_invalid_and_inactive_credentials_share_a_generic_error(self) -> None:
        invalid_response = self.client.post(
            reverse("accounts:login"),
            {"username": self.borrower.username, "password": "wrong-password"},
        )
        self.assertEqual(invalid_response.status_code, 200)
        self.assertContains(invalid_response, "Invalid username or password.")
        self.assertNotIn(SESSION_KEY, self.client.session)

        inactive_response = self.client.post(
            reverse("accounts:login"),
            {"username": self.inactive.username, "password": PASSWORD},
        )
        self.assertEqual(inactive_response.status_code, 200)
        self.assertContains(inactive_response, "Invalid username or password.")
        self.assertNotIn(SESSION_KEY, self.client.session)

    def test_home_and_role_destinations_enforce_authentication_and_role(self) -> None:
        anonymous_home = self.client.get(reverse("accounts:home"))
        self.assertRedirects(
            anonymous_home,
            f"{reverse('accounts:login')}?next=/",
            fetch_redirect_response=False,
        )
        anonymous_portal = self.client.get(reverse("portal:home"))
        self.assertEqual(anonymous_portal.status_code, 302)
        self.assertIn(reverse("accounts:login"), anonymous_portal.headers["Location"])

        self.client.force_login(self.borrower)
        self.assertEqual(self.client.get(reverse("portal:home")).status_code, 200)
        self.assertEqual(self.client.get(reverse("operations:dashboard")).status_code, 403)

        self.client.force_login(self.admin)
        self.assertEqual(self.client.get(reverse("operations:dashboard")).status_code, 200)
        self.assertEqual(self.client.get(reverse("portal:home")).status_code, 403)

    def test_django_permission_flags_do_not_bypass_the_product_role(self) -> None:
        self.borrower.is_staff = True
        self.borrower.is_superuser = True
        self.borrower.save(update_fields=["is_staff", "is_superuser"])
        self.client.force_login(self.borrower)
        response = self.client.get(reverse("operations:dashboard"))
        self.assertEqual(response.status_code, 403)

    def test_inactive_existing_session_is_denied_and_invalidated(self) -> None:
        self.client.force_login(self.borrower)
        User.objects.filter(pk=self.borrower.pk).update(is_active=False)
        response = self.client.get(reverse("portal:home"))
        self.assertEqual(response.status_code, 403)
        self.assertNotIn(SESSION_KEY, self.client.session)

    def test_logout_is_post_only_and_csrf_protected(self) -> None:
        csrf_client = Client(enforce_csrf_checks=True)
        csrf_client.force_login(self.borrower)
        portal_response = csrf_client.get(reverse("portal:home"))
        self.assertEqual(portal_response.status_code, 200)

        self.assertEqual(csrf_client.get(reverse("accounts:logout")).status_code, 405)
        self.assertEqual(csrf_client.post(reverse("accounts:logout")).status_code, 403)

        csrf_token: str = csrf_client.cookies["csrftoken"].value
        logout_response = csrf_client.post(
            reverse("accounts:logout"),
            HTTP_X_CSRFTOKEN=csrf_token,
        )
        self.assertRedirects(
            logout_response, reverse("accounts:login"), fetch_redirect_response=False
        )
        self.assertNotIn(SESSION_KEY, csrf_client.session)

    @override_settings(DEBUG=True)
    def test_debug_font_preview_remains_reachable_from_authentication_routes(self) -> None:
        response = self.client.get(reverse("frontend-test"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, reverse("accounts:home"))
        self.assertContains(response, "Application home")

    @override_settings(DEBUG=False)
    def test_font_preview_remains_hidden_when_debug_is_disabled(self) -> None:
        response = self.client.get(reverse("frontend-test"))
        self.assertEqual(response.status_code, 404)


@override_settings(ROOT_URLCONF=__name__)
class OwnershipAccessTests(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.owner: User = create_account("record_owner", UserRole.BASIC_USER, True)
        cls.other_user: User = create_account("other_owner", UserRole.BASIC_USER, True)
        submitted_at = timezone.now()
        submitted_on = timezone.localdate(submitted_at)
        cls.borrow_request: BorrowRequest = BorrowRequest.objects.create(
            owner=cls.owner,
            purpose="Fictional ownership check",
            submitted_at=submitted_at,
            submitted_on=submitted_on,
            desired_due_date=submitted_on + timedelta(days=1),
            agreed_due_date=submitted_on + timedelta(days=1),
            max_loan_days_applied=7,
            max_quantity_applied=3,
            status=RequestStatus.PENDING,
            decision_reason="",
        )

    def test_direct_cross_owner_request_returns_404_without_disclosure(self) -> None:
        self.client.force_login(self.other_user)
        response = self.client.get(f"/owned-requests/{self.borrow_request.pk}/")
        self.assertEqual(response.status_code, 404)

        self.client.force_login(self.owner)
        owner_response = self.client.get(f"/owned-requests/{self.borrow_request.pk}/")
        self.assertEqual(owner_response.status_code, 200)
        self.assertEqual(owner_response.content.decode(), str(self.borrow_request.pk))


class AdminCreationCommandTests(TestCase):
    def test_command_creates_only_an_active_admin_and_profile(self) -> None:
        output = StringIO()
        with patch(
            "accounts.management.commands.create_admin.getpass",
            side_effect=[PASSWORD, PASSWORD],
        ):
            call_command(
                "create_admin",
                username="setup_admin",
                first_name="Setup",
                last_name="Administrator",
                email="setup_admin@example.invalid",
                stdout=output,
            )

        admin: User = User.objects.get(username="setup_admin")
        self.assertEqual(admin.role, UserRole.ADMIN)
        self.assertTrue(admin.is_active)
        self.assertFalse(admin.is_staff)
        self.assertFalse(admin.is_superuser)
        self.assertTrue(admin.check_password(PASSWORD))
        self.assertTrue(Profile.objects.filter(user=admin).exists())
        self.assertIn("Created ADMIN account 'setup_admin'.", output.getvalue())
        self.assertNotIn(PASSWORD, output.getvalue())

    def test_command_rejects_mismatch_and_weak_password_without_partial_rows(self) -> None:
        with (
            patch(
                "accounts.management.commands.create_admin.getpass",
                side_effect=[PASSWORD, "different-password"],
            ),
            self.assertRaisesMessage(CommandError, "Passwords do not match"),
        ):
            call_command(
                "create_admin",
                username="mismatch_admin",
                first_name="Mismatch",
                last_name="Administrator",
                email="mismatch@example.invalid",
            )
        self.assertFalse(User.objects.filter(username="mismatch_admin").exists())

        with (
            patch(
                "accounts.management.commands.create_admin.getpass",
                side_effect=["123", "123"],
            ),
            self.assertRaises(CommandError),
        ):
            call_command(
                "create_admin",
                username="weak_admin",
                first_name="Weak",
                last_name="Administrator",
                email="weak@example.invalid",
            )
        self.assertFalse(User.objects.filter(username="weak_admin").exists())
        self.assertFalse(Profile.objects.filter(user__username="weak_admin").exists())
