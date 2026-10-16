"""Verify settings, snapshots, validation, and transactional audit behavior."""

from datetime import date, timedelta

from django.core.exceptions import ImproperlyConfigured, PermissionDenied, ValidationError
from django.db import IntegrityError, connection, transaction
from django.test import TestCase
from django.utils import timezone

from accounts.models import User
from borrowing.models import BorrowRequest, RequestItem
from operations.audit import write_audit
from operations.models import AuditAction, AuditLog, AuditTarget, SystemSetting
from operations.queries import get_loan_limits
from operations.services import update_settings
from operations.tests.records import CatalogRecords, create_catalog_records, create_request
from operations.validation import (
    LoanLimits,
    RequestedItem,
    validate_requested_due_date,
    validate_requested_items,
    validate_revised_due_date,
)


class SharedServiceTests(TestCase):
    records: CatalogRecords

    def setUp(self) -> None:
        self.records = create_catalog_records()

    def test_settings_update_is_audited_and_preserves_existing_snapshot(self) -> None:
        request_item: RequestItem = create_request(
            self.records.borrower.pk, self.records.item.pk, timezone.now()
        )
        original_limits: LoanLimits = get_loan_limits()
        setting: SystemSetting = update_settings(self.records.admin.pk, 4, 2)
        self.assertEqual(
            (setting.max_loan_days, setting.max_quantity_per_item, setting.updated_by_id),
            (4, 2, self.records.admin.pk),
        )
        self.assertEqual(get_loan_limits(), LoanLimits(max_loan_days=4, max_quantity_per_item=2))
        request: BorrowRequest = BorrowRequest.objects.get(pk=request_item.request_id)
        self.assertEqual((request.max_loan_days_applied, request.max_quantity_applied), (7, 3))
        self.assertEqual(original_limits, LoanLimits(max_loan_days=7, max_quantity_per_item=3))
        audit: AuditLog = AuditLog.objects.get(action=AuditAction.SETTINGS_UPDATED)
        self.assertEqual(
            (audit.actor_id, audit.target_id, audit.target_model),
            (self.records.admin.pk, 1, AuditTarget.SYSTEM_SETTING),
        )
        self.assertIn("7 -> 4", audit.summary)

    def test_wrong_role_inactive_actor_and_invalid_limits_cannot_change_settings(self) -> None:
        User.objects.filter(pk=self.records.borrower.pk).update(is_staff=True, is_superuser=True)
        with self.assertRaises(PermissionDenied):
            update_settings(self.records.borrower.pk, 4, 2)
        User.objects.filter(pk=self.records.admin.pk).update(is_active=False)
        with self.assertRaises(PermissionDenied):
            update_settings(self.records.admin.pk, 4, 2)
        with self.assertRaises(ValidationError):
            update_settings(self.records.admin.pk, 0, 2)
        self.assertEqual(get_loan_limits(), LoanLimits(max_loan_days=7, max_quantity_per_item=3))
        self.assertFalse(AuditLog.objects.filter(action=AuditAction.SETTINGS_UPDATED).exists())

    def test_database_audit_failure_rolls_back_settings(self) -> None:
        # PostgreSQL rejects the audit INSERT; no mocked writer or production hook.
        with connection.cursor() as cursor:
            cursor.execute(
                "ALTER TABLE operations_auditlog ADD CONSTRAINT test_reject_settings_audit "
                "CHECK (action <> 'SETTINGS_UPDATED')"
            )
        with self.assertRaises(IntegrityError):
            update_settings(self.records.admin.pk, 4, 2)
        self.assertEqual(get_loan_limits(), LoanLimits(max_loan_days=7, max_quantity_per_item=3))
        self.assertFalse(AuditLog.objects.filter(action=AuditAction.SETTINGS_UPDATED).exists())

    def test_missing_singleton_is_an_explicit_configuration_error(self) -> None:
        SystemSetting.objects.get(pk=1).delete()
        with self.assertRaisesMessage(ImproperlyConfigured, "row 1 is missing"):
            get_loan_limits()
        with self.assertRaisesMessage(ImproperlyConfigured, "row 1 is missing"):
            update_settings(self.records.admin.pk, 4, 2)
        self.assertFalse(SystemSetting.objects.exists())

    def test_audit_validates_target_and_rolls_back_enclosing_business_change(self) -> None:
        with self.assertRaises(ValidationError), transaction.atomic():
            SystemSetting.objects.filter(pk=1).update(max_loan_days=4)
            write_audit(
                self.records.admin.pk,
                AuditAction.SETTINGS_UPDATED,
                AuditTarget.SYSTEM_SETTING,
                999,
                "No target",
            )
        self.assertEqual(get_loan_limits().max_loan_days, 7)
        with self.assertRaises(ValidationError):
            write_audit(
                self.records.admin.pk,
                AuditAction.SETTINGS_UPDATED,
                AuditTarget.CATEGORY,
                self.records.category.pk,
                "Wrong target",
            )
        with self.assertRaises(ValidationError):
            write_audit(
                self.records.admin.pk,
                AuditAction.SETTINGS_INITIALIZED,
                AuditTarget.SYSTEM_SETTING,
                1,
                "Invalid actor kind",
            )
        audit: AuditLog = write_audit(
            self.records.admin.pk,
            AuditAction.CATEGORY_UPDATED,
            AuditTarget.CATEGORY,
            self.records.category.pk,
            "  <b>Description</b> updated\nfor test category.  ",
        )
        self.assertEqual(audit.summary, "Description updated for test category.")
        User.objects.filter(pk=self.records.admin.pk).update(is_active=False)
        with self.assertRaises(PermissionDenied):
            write_audit(
                self.records.admin.pk,
                AuditAction.CATEGORY_UPDATED,
                AuditTarget.CATEGORY,
                self.records.category.pk,
                "Inactive actor",
            )

    def test_new_limits_validate_dates_and_all_rows_without_writes(self) -> None:
        update_settings(self.records.admin.pk, 3, 2)
        limits: LoanLimits = get_loan_limits()
        submitted_on: date = date(2028, 2, 28)
        self.assertEqual(
            validate_requested_due_date(submitted_on, date(2028, 3, 2), limits), date(2028, 3, 2)
        )
        for invalid_due in (submitted_on, submitted_on - timedelta(days=1), date(2028, 3, 3)):
            with self.subTest(due=invalid_due), self.assertRaises(ValidationError):
                validate_requested_due_date(submitted_on, invalid_due, limits)
        self.assertEqual(
            validate_revised_due_date(submitted_on, date(2028, 3, 1), date(2028, 3, 1), limits),
            date(2028, 3, 1),
        )
        with self.assertRaises(ValidationError):
            validate_revised_due_date(submitted_on, date(2028, 2, 29), date(2028, 3, 1), limits)
        valid_items: tuple[RequestedItem, ...] = (
            RequestedItem(catalog_item_id=self.records.item.pk, quantity=2),
        )
        self.assertEqual(validate_requested_items(valid_items, limits), valid_items)
        for invalid_items in (
            (),
            valid_items + valid_items,
            (
                RequestedItem(catalog_item_id=1, quantity=1),
                RequestedItem(catalog_item_id=2, quantity=1),
                RequestedItem(catalog_item_id=3, quantity=3),
            ),
            tuple(RequestedItem(catalog_item_id=index, quantity=1) for index in range(1, 5)),
        ):
            with self.subTest(items=invalid_items), self.assertRaises(ValidationError):
                validate_requested_items(invalid_items, limits)
        self.assertFalse(BorrowRequest.objects.exists())
        self.assertFalse(RequestItem.objects.exists())
