"""Observable T09 student registration, profile management, and portal layout checks."""

from unittest.mock import patch

from django.contrib.auth import SESSION_KEY
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse

from accounts.models import Profile, User, UserRole
from operations.models import AuditAction, AuditLog, AuditTarget

PASSWORD: str = "Correct-Horse-Battery-Staple-2026!"


def create_account(username: str, role: UserRole, is_active: bool) -> User:
    """Create a fictional test user with the required Profile record."""
    user: User = User.objects.create_user(
        username=username,
        password=PASSWORD,
        first_name="Fictional",
        last_name="Student",
        email=f"{username}@example.invalid",
        role=role,
        is_active=is_active,
    )
    Profile.objects.create(user=user, contact_number="0912-345-6789")
    return user


class BorrowerRegistrationTests(TestCase):
    """Test public student self-registration under the accounts:register route."""

    @classmethod
    def setUpTestData(cls) -> None:
        cls.existing_borrower: User = create_account("existing_user", UserRole.BASIC_USER, True)
        cls.admin: User = create_account("existing_admin", UserRole.ADMIN, True)

    def test_anonymous_user_can_view_registration_form(self) -> None:
        response = self.client.get(reverse("accounts:register"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'data-testid="register-page"')
        self.assertContains(response, 'data-testid="register-submit"')
        self.assertContains(response, 'name="username"')
        self.assertContains(response, 'name="first_name"')
        self.assertContains(response, 'name="last_name"')
        self.assertContains(response, 'name="email"')
        self.assertContains(response, 'name="contact_number"')
        self.assertContains(response, 'name="password1"')
        self.assertContains(response, 'name="password2"')

    def test_authenticated_users_redirected_from_registration(self) -> None:
        self.client.force_login(self.admin)
        admin_response = self.client.get(reverse("accounts:register"))
        self.assertRedirects(admin_response, reverse("operations:dashboard"))

        self.client.force_login(self.existing_borrower)
        borrower_response = self.client.get(reverse("accounts:register"))
        self.assertRedirects(borrower_response, reverse("portal:home"))

    def test_successful_registration_creates_basic_user_and_profile_atomically(self) -> None:
        registration_data: dict[str, str] = {
            "username": "new_student",
            "first_name": "Maria",
            "last_name": "Santos",
            "email": "maria.santos@bulsu.edu.ph",
            "contact_number": "0918-123-4567",
            "password1": "Secure-Student-Pass-2026!",
            "password2": "Secure-Student-Pass-2026!",
        }
        response = self.client.post(reverse("accounts:register"), registration_data)
        self.assertRedirects(response, reverse("accounts:login"))

        user: User = User.objects.get(username="new_student")
        self.assertEqual(user.first_name, "Maria")
        self.assertEqual(user.last_name, "Santos")
        self.assertEqual(user.email, "maria.santos@bulsu.edu.ph")
        self.assertEqual(user.role, UserRole.BASIC_USER)
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

        profile: Profile = Profile.objects.get(user=user)
        self.assertEqual(profile.contact_number, "0918-123-4567")

        # Verify new credentials can log in
        login_success: bool = self.client.login(
            username="new_student", password="Secure-Student-Pass-2026!"
        )
        self.assertTrue(login_success)

        # Verify audit log was recorded atomically
        audit_log: AuditLog = AuditLog.objects.get(
            action=AuditAction.ACCOUNT_CREATED,
            target_model=AuditTarget.USER,
            target_id=user.pk,
        )
        self.assertEqual(audit_log.actor_id, user.pk)
        self.assertEqual(audit_log.summary, "Basic-user account self-registered.")

    def test_registration_rejects_self_promotion_and_role_forgery(self) -> None:
        tampered_data: dict[str, str] = {
            "username": "attacker",
            "first_name": "Mallory",
            "last_name": "Attacker",
            "email": "mallory@bulsu.edu.ph",
            "contact_number": "0911-000-0000",
            "password1": "Secure-Student-Pass-2026!",
            "password2": "Secure-Student-Pass-2026!",
            "role": "ADMIN",
            "is_staff": "true",
            "is_superuser": "true",
        }
        response = self.client.post(reverse("accounts:register"), tampered_data)
        self.assertRedirects(response, reverse("accounts:login"))

        user: User = User.objects.get(username="attacker")
        self.assertEqual(user.role, UserRole.BASIC_USER)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_registration_validation_errors(self) -> None:
        cases: list[tuple[dict[str, str], str]] = [
            (
                {
                    "username": "",
                    "first_name": "Maria",
                    "last_name": "Santos",
                    "email": "maria@example.invalid",
                    "password1": "Valid-Pass-2026!",
                    "password2": "Valid-Pass-2026!",
                },
                "Username cannot be blank.",
            ),
            (
                {
                    "username": "existing_user",
                    "first_name": "Maria",
                    "last_name": "Santos",
                    "email": "maria@example.invalid",
                    "password1": "Valid-Pass-2026!",
                    "password2": "Valid-Pass-2026!",
                },
                "An account with this username already exists.",
            ),
            (
                {
                    "username": "new_user",
                    "first_name": "Maria",
                    "last_name": "Santos",
                    "email": "existing_user@example.invalid",
                    "password1": "Valid-Pass-2026!",
                    "password2": "Valid-Pass-2026!",
                },
                "An account with this email already exists.",
            ),
            (
                {
                    "username": "new_user",
                    "first_name": "Maria",
                    "last_name": "Santos",
                    "email": "maria@example.invalid",
                    "password1": "Valid-Pass-2026!",
                    "password2": "Mismatched-Pass-2026!",
                },
                "The two passwords do not match.",
            ),
            (
                {
                    "username": "new_user",
                    "first_name": "Maria",
                    "last_name": "Santos",
                    "email": "maria@example.invalid",
                    "password1": "short",
                    "password2": "short",
                },
                "at least 8 characters",
            ),
        ]
        for data, expected_error in cases:
            with self.subTest(error=expected_error):
                response = self.client.post(reverse("accounts:register"), data)
                self.assertEqual(response.status_code, 200)
                self.assertContains(response, expected_error)

    def test_invalid_username_returns_field_errors_without_writes(self) -> None:
        user_count: int = User.objects.count()
        profile_count: int = Profile.objects.count()
        audit_count: int = AuditLog.objects.count()
        for username in ("review student", "review/student", "review\u00bc"):
            with self.subTest(username=username):
                response = self.client.post(
                    reverse("accounts:register"),
                    {
                        "username": username,
                        "first_name": "Review",
                        "last_name": "Student",
                        "email": "review.student@example.invalid",
                        "contact_number": "",
                        "password1": PASSWORD,
                        "password2": PASSWORD,
                    },
                )
                self.assertEqual(response.status_code, 200)
                self.assertContains(response, "Enter a valid username.")
                self.assertEqual(
                    response.context["form"].errors.as_data()["username"][0].code, "invalid"
                )
                self.assertEqual(User.objects.count(), user_count)
                self.assertEqual(Profile.objects.count(), profile_count)
                self.assertEqual(AuditLog.objects.count(), audit_count)

    def test_registration_rolls_back_if_audit_fails(self) -> None:
        registration_data: dict[str, str] = {
            "username": "rollback_student",
            "first_name": "Maria",
            "last_name": "Santos",
            "email": "rollback@bulsu.edu.ph",
            "contact_number": "0918-123-4567",
            "password1": "Secure-Student-Pass-2026!",
            "password2": "Secure-Student-Pass-2026!",
        }
        with patch("accounts.services.write_audit", side_effect=ValidationError("Audit failure")):
            with self.assertRaises(ValidationError):
                self.client.post(reverse("accounts:register"), registration_data)

        self.assertFalse(User.objects.filter(username="rollback_student").exists())
        self.assertFalse(Profile.objects.filter(contact_number="0918-123-4567").exists())


class BorrowerProfileTests(TestCase):
    """Test basic-user profile view and updates under the portal:profile route."""

    @classmethod
    def setUpTestData(cls) -> None:
        cls.borrower: User = create_account("juan_borrower", UserRole.BASIC_USER, True)
        cls.other_borrower: User = create_account("other_student", UserRole.BASIC_USER, True)
        cls.admin: User = create_account("portal_admin", UserRole.ADMIN, True)
        cls.inactive_borrower: User = create_account("inactive_student", UserRole.BASIC_USER, False)

    def test_borrower_can_view_own_profile(self) -> None:
        self.client.force_login(self.borrower)
        response = self.client.get(reverse("portal:profile"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'data-testid="own-profile"')
        self.assertContains(response, 'data-testid="profile-username"')
        self.assertContains(response, self.borrower.username)
        self.assertContains(response, self.borrower.email)
        self.assertContains(response, self.borrower.first_name)
        self.assertContains(response, self.borrower.last_name)
        self.assertContains(response, self.borrower.profile.contact_number)
        self.assertContains(response, 'data-testid="profile-submit"')

    def test_admin_cannot_access_borrower_profile(self) -> None:
        self.client.force_login(self.admin)
        response = self.client.get(reverse("portal:profile"))
        self.assertEqual(response.status_code, 403)
        post_response = self.client.post(
            reverse("portal:profile"),
            {
                "first_name": "Test",
                "last_name": "Test",
                "email": "test@example.invalid",
                "contact_number": "",
            },
        )
        self.assertEqual(post_response.status_code, 403)

    def test_anonymous_redirected_to_login(self) -> None:
        response = self.client.get(reverse("portal:profile"))
        self.assertRedirects(
            response, f"{reverse('accounts:login')}?next={reverse('portal:profile')}"
        )

    def test_deactivated_borrower_denied_with_session_cleared(self) -> None:
        self.client.force_login(self.inactive_borrower)
        response = self.client.get(reverse("portal:profile"))
        self.assertEqual(response.status_code, 403)
        self.assertNotIn(SESSION_KEY, self.client.session)

    def test_borrower_can_update_personal_details_successfully(self) -> None:
        self.client.force_login(self.borrower)
        update_data: dict[str, str] = {
            "first_name": "Juanito",
            "last_name": "Dela Cruz",
            "email": "juanito.delacruz@bulsu.edu.ph",
            "contact_number": "0999-888-7777",
        }
        response = self.client.post(reverse("portal:profile"), update_data)
        self.assertRedirects(response, reverse("portal:profile"))

        self.borrower.refresh_from_db()
        self.assertEqual(self.borrower.first_name, "Juanito")
        self.assertEqual(self.borrower.last_name, "Dela Cruz")
        self.assertEqual(self.borrower.email, "juanito.delacruz@bulsu.edu.ph")
        self.assertEqual(self.borrower.profile.contact_number, "0999-888-7777")

        # Verify audit log was recorded
        audit_log: AuditLog = AuditLog.objects.get(
            action=AuditAction.ACCOUNT_UPDATED,
            target_model=AuditTarget.USER,
            target_id=self.borrower.pk,
        )
        self.assertEqual(audit_log.actor_id, self.borrower.pk)
        self.assertEqual(audit_log.summary, "Borrower updated personal profile details.")

    def test_profile_update_rejects_self_promotion_and_protected_field_tampering(self) -> None:
        self.client.force_login(self.borrower)
        tampered_data: dict[str, str] = {
            "first_name": "Juan",
            "last_name": "Student",
            "email": self.borrower.email,
            "contact_number": "0912-345-6789",
            "username": "hacked_user",
            "role": "ADMIN",
            "is_staff": "true",
            "is_superuser": "true",
            "is_active": "false",
        }
        response = self.client.post(reverse("portal:profile"), tampered_data)
        self.assertRedirects(response, reverse("portal:profile"))

        self.borrower.refresh_from_db()
        self.assertEqual(self.borrower.username, "juan_borrower")
        self.assertEqual(self.borrower.role, UserRole.BASIC_USER)
        self.assertTrue(self.borrower.is_active)
        self.assertFalse(self.borrower.is_staff)
        self.assertFalse(self.borrower.is_superuser)

    def test_profile_update_validation_errors(self) -> None:
        self.client.force_login(self.borrower)
        cases: list[tuple[dict[str, str], str]] = [
            (
                {
                    "first_name": "",
                    "last_name": "Student",
                    "email": "valid@bulsu.edu.ph",
                    "contact_number": "",
                },
                "First name cannot be blank.",
            ),
            (
                {
                    "first_name": "Juan",
                    "last_name": "",
                    "email": "valid@bulsu.edu.ph",
                    "contact_number": "",
                },
                "Last name cannot be blank.",
            ),
            (
                {
                    "first_name": "Juan",
                    "last_name": "Student",
                    "email": "",
                    "contact_number": "",
                },
                "Email address cannot be blank.",
            ),
            (
                {
                    "first_name": "Juan",
                    "last_name": "Student",
                    "email": self.other_borrower.email,
                    "contact_number": "",
                },
                "An account with this email already exists.",
            ),
            (
                {
                    "first_name": "Juan",
                    "last_name": "Student",
                    "email": "not-an-email",
                    "contact_number": "",
                },
                "Enter a valid email address.",
            ),
        ]
        for data, expected_error in cases:
            with self.subTest(error=expected_error):
                response = self.client.post(reverse("portal:profile"), data)
                self.assertEqual(response.status_code, 200)
                self.assertContains(response, expected_error)

    def test_profile_form_preserves_unmodified_email(self) -> None:
        self.client.force_login(self.borrower)
        response = self.client.post(
            reverse("portal:profile"),
            {
                "first_name": "UpdatedName",
                "last_name": "Student",
                "email": self.borrower.email,
                "contact_number": "0999-111-2222",
            },
        )
        self.assertRedirects(response, reverse("portal:profile"))
        self.borrower.refresh_from_db()
        self.assertEqual(self.borrower.first_name, "UpdatedName")

    def test_profile_update_rolls_back_if_audit_fails(self) -> None:
        self.client.force_login(self.borrower)
        update_data: dict[str, str] = {
            "first_name": "RollbackName",
            "last_name": "Student",
            "email": "rollback@bulsu.edu.ph",
            "contact_number": "0911-222-3333",
        }
        with patch("accounts.services.write_audit", side_effect=ValidationError("Audit failure")):
            with self.assertRaises(ValidationError):
                self.client.post(reverse("portal:profile"), update_data)

        self.borrower.refresh_from_db()
        self.assertNotEqual(self.borrower.first_name, "RollbackName")
