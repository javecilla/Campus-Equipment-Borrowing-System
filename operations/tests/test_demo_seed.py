"""Real PostgreSQL account seeding, HTTP access, preservation and rollback checks."""

import os
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from django.apps import apps
from django.core import serializers
from django.core.exceptions import ValidationError
from django.core.management import call_command
from django.core.management.base import CommandError
from django.db import IntegrityError, connection
from django.db.models import Model
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from accounts.models import Profile, User, UserRole
from borrowing.models import BorrowRequest, Loan
from inventory.models import CatalogItem, Category, EquipmentUnit, MaintenanceRecord
from operations.demo_seed import DEMO_ADMIN, DEMO_BORROWERS, seed_demo_data
from operations.models import AuditLog
from operations.tests.records import create_issued_records

PASSWORD = "Orchard-Telescope-Notebook-2026!"


class DemonstrationSeedTests(TestCase):
    def test_command_creates_realistic_accounts_without_equipment_or_transactions(self) -> None:
        output = StringIO()
        with TemporaryDirectory() as directory:
            (Path(directory) / ".env.local").write_text("", encoding="utf-8")
            with (
                override_settings(BASE_DIR=Path(directory)),
                patch.dict(os.environ, {"SEED_ACCOUNT_PASSWORD": PASSWORD}),
            ):
                call_command("seed_demo_data", stdout=output)
        self.assertNotIn(PASSWORD, output.getvalue())
        self.assertEqual(User.objects.count(), 9)
        self.assertEqual(Profile.objects.count(), 9)
        self.assertEqual(User.objects.filter(role=UserRole.ADMIN).count(), 1)
        self.assertEqual(User.objects.filter(role=UserRole.BASIC_USER).count(), 8)
        for model in (Category, CatalogItem, EquipmentUnit, MaintenanceRecord, BorrowRequest, Loan):
            self.assertEqual(model.objects.count(), 0)
        for identity in (DEMO_ADMIN, *DEMO_BORROWERS):
            user: User = User.objects.get(username=identity.username)
            self.assertEqual(
                (user.first_name, user.last_name), (identity.first_name, identity.last_name)
            )
            self.assertEqual(user.email, f"{identity.username}@example.invalid")
            self.assertTrue(user.is_active)
            self.assertFalse(user.is_staff)
            self.assertFalse(user.is_superuser)
            self.assertTrue(user.check_password(PASSWORD))
            client = Client()
            response = client.post(
                reverse("accounts:login"), {"username": identity.username, "password": PASSWORD}
            )
            destination: str = (
                "operations:dashboard" if user.role == UserRole.ADMIN else "portal:home"
            )
            forbidden: str = (
                "portal:home" if user.role == UserRole.ADMIN else "operations:dashboard"
            )
            self.assertRedirects(response, reverse(destination))
            self.assertEqual(client.get(reverse(forbidden)).status_code, 403)

    def test_existing_inventory_and_history_remain_identical_and_repeat_is_rejected(self) -> None:
        create_issued_records()
        models: tuple[type[Model], ...] = tuple(
            model
            for model in apps.get_models()
            if model._meta.app_label in ("accounts", "inventory", "borrowing", "operations")
        )
        baseline: tuple[tuple[type[Model], tuple[int, ...], str], ...] = tuple(
            (
                model,
                tuple(model.objects.order_by("pk").values_list("pk", flat=True)),
                serializers.serialize("json", model.objects.order_by("pk")),
            )
            for model in models
        )
        seed_demo_data(PASSWORD)
        for model, identifiers, original in baseline:
            self.assertEqual(
                serializers.serialize(
                    "json", model.objects.filter(pk__in=identifiers).order_by("pk")
                ),
                original,
                model.__name__,
            )
        counts: tuple[int, int] = (User.objects.count(), AuditLog.objects.count())
        with self.assertRaisesMessage(ValidationError, "already exist"):
            seed_demo_data(PASSWORD)
        self.assertEqual((User.objects.count(), AuditLog.objects.count()), counts)

    def test_audit_failure_rolls_back_all_accounts(self) -> None:
        original_audits: int = AuditLog.objects.count()
        with connection.cursor() as cursor:
            cursor.execute("SET CONSTRAINTS ALL IMMEDIATE")
            cursor.execute(
                "ALTER TABLE operations_auditlog ADD CONSTRAINT test_clean_demo_audit CHECK (action <> 'ACCOUNT_CREATED')"
            )
        with self.assertRaises(IntegrityError):
            seed_demo_data(PASSWORD)
        self.assertEqual(User.objects.count(), 0)
        self.assertEqual(Profile.objects.count(), 0)
        self.assertEqual(AuditLog.objects.count(), original_audits)

    def test_invalid_password_or_existing_email_creates_no_accounts(self) -> None:
        with self.assertRaises(ValidationError):
            seed_demo_data("123")
        self.assertEqual(User.objects.count(), 0)
        existing: User = User.objects.create_user(
            username="existing_user",
            email=f"{DEMO_ADMIN.username.upper()}@example.invalid",
            password=PASSWORD,
        )
        with self.assertRaisesMessage(ValidationError, "already exist"):
            seed_demo_data(PASSWORD)
        self.assertEqual(User.objects.count(), 1)
        self.assertTrue(User.objects.get(pk=existing.pk).check_password(PASSWORD))

    def test_blank_private_password_creates_no_accounts(self) -> None:
        with TemporaryDirectory() as directory:
            (Path(directory) / ".env.local").write_text("", encoding="utf-8")
            with (
                override_settings(BASE_DIR=Path(directory)),
                patch.dict(os.environ, {"SEED_ACCOUNT_PASSWORD": " "}),
                self.assertRaisesMessage(CommandError, "SEED_ACCOUNT_PASSWORD is required"),
            ):
                call_command("seed_demo_data")
        self.assertEqual(User.objects.count(), 0)
