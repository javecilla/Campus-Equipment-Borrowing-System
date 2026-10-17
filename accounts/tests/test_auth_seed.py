"""Real ORM and HTTP verification of the two-account authentication seed."""

import os
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from django.contrib.auth import SESSION_KEY
from django.core.exceptions import ValidationError
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from accounts.models import Profile, User, UserRole
from accounts.seeding import AUTH_ADMIN_USERNAME, AUTH_BASIC_USERNAME, seed_auth_accounts

ADMIN_PASSWORD = "Orchard-Lantern-Compass-2026!"
BASIC_PASSWORD = "River-Copper-Telescope-2026!"


class AuthenticationSeedTests(TestCase):
    def test_command_accounts_support_role_access_and_csrf_logout(self) -> None:
        output = StringIO()
        with TemporaryDirectory() as directory:
            base_dir: Path = Path(directory)
            (base_dir / ".env.local").write_text(
                f"SEED_ACCOUNT_PASSWORD='{ADMIN_PASSWORD}'\n", encoding="utf-8"
            )
            process_values: dict[str, str] = {
                key: value for key, value in os.environ.items() if key != "SEED_ACCOUNT_PASSWORD"
            }
            with (
                override_settings(BASE_DIR=base_dir),
                patch.dict(os.environ, process_values, clear=True),
            ):
                call_command("seed_auth_accounts", stdout=output)

        for username, password, role, destination, forbidden in [
            (
                AUTH_ADMIN_USERNAME,
                ADMIN_PASSWORD,
                UserRole.ADMIN,
                "operations:dashboard",
                "portal:home",
            ),
            (
                AUTH_BASIC_USERNAME,
                ADMIN_PASSWORD,
                UserRole.BASIC_USER,
                "portal:home",
                "operations:dashboard",
            ),
        ]:
            with self.subTest(username=username):
                user: User = User.objects.get(username=username)
                self.assertEqual(user.role, role)
                self.assertTrue(user.is_active)
                self.assertFalse(user.is_staff)
                self.assertFalse(user.is_superuser)
                self.assertTrue(user.check_password(password))
                self.assertTrue(Profile.objects.filter(user=user).exists())
                self.assertNotIn(password, output.getvalue())
                client = Client(enforce_csrf_checks=True)
                client.get(reverse("accounts:login"))
                response = client.post(
                    reverse("accounts:login"),
                    {"username": username, "password": password},
                    HTTP_X_CSRFTOKEN=client.cookies["csrftoken"].value,
                )
                self.assertRedirects(response, reverse(destination))
                self.assertEqual(client.get(reverse(forbidden)).status_code, 403)
                logout_response = client.post(
                    reverse("accounts:logout"),
                    HTTP_X_CSRFTOKEN=client.cookies["csrftoken"].value,
                )
                self.assertRedirects(logout_response, reverse("accounts:login"))
                self.assertNotIn(SESSION_KEY, client.session)
                self.assertEqual(client.get(reverse(destination)).status_code, 302)

    def test_invalid_basic_password_rolls_back_both_accounts_and_profiles(self) -> None:
        with self.assertRaises(ValidationError):
            seed_auth_accounts(ADMIN_PASSWORD, "123")
        self.assertEqual(User.objects.count(), 0)
        self.assertEqual(Profile.objects.count(), 0)

    def test_existing_basic_account_is_preserved_and_prevents_admin_creation(self) -> None:
        existing: User = User.objects.create_user(
            username=AUTH_BASIC_USERNAME,
            password=BASIC_PASSWORD,
            role=UserRole.BASIC_USER,
            is_active=False,
        )
        with self.assertRaisesMessage(ValidationError, "usernames already exist"):
            seed_auth_accounts(ADMIN_PASSWORD, BASIC_PASSWORD)
        existing.refresh_from_db()
        self.assertFalse(existing.is_active)
        self.assertTrue(existing.check_password(BASIC_PASSWORD))
        self.assertFalse(User.objects.filter(username=AUTH_ADMIN_USERNAME).exists())
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(Profile.objects.count(), 0)

    def test_missing_or_blank_seed_password_creates_no_accounts(self) -> None:
        process_values: dict[str, str] = {
            key: value for key, value in os.environ.items() if key != "SEED_ACCOUNT_PASSWORD"
        }
        with TemporaryDirectory() as directory:
            base_dir: Path = Path(directory)
            for content in ["", "SEED_ACCOUNT_PASSWORD=' '\n"]:
                with self.subTest(content=content):
                    (base_dir / ".env.local").write_text(content, encoding="utf-8")
                    with (
                        override_settings(BASE_DIR=base_dir),
                        patch.dict(os.environ, process_values, clear=True),
                        self.assertRaisesMessage(CommandError, "SEED_ACCOUNT_PASSWORD is required"),
                    ):
                        call_command("seed_auth_accounts")
        self.assertEqual(User.objects.count(), 0)
        self.assertEqual(Profile.objects.count(), 0)
