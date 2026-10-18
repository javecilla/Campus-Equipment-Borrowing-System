"""Real PostgreSQL checks for independently restoring catalog master records."""

from django.core.exceptions import PermissionDenied
from django.db import IntegrityError, connection
from django.test import Client, TestCase
from django.urls import reverse

from accounts.models import User, UserRole
from inventory.models import CatalogItem, Category, EquipmentUnit, UnitStatus
from inventory.services import (
    archive_catalog_item,
    archive_category,
    restore_catalog_item,
    restore_category,
)
from inventory.tests.test_catalog_management import create_user
from operations.models import AuditAction, AuditLog, AuditTarget
from operations.tests.records import IssuedRecords, create_issued_records


class CatalogRestoreTests(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.records: IssuedRecords = create_issued_records()
        cls.admin: User = cls.records.catalog.admin
        cls.category: Category = cls.records.catalog.category
        cls.item: CatalogItem = cls.records.catalog.item
        cls.inactive_admin: User = create_user("inactive_restore_admin", UserRole.ADMIN, False)
        cls.archived_sibling: CatalogItem = CatalogItem.objects.create(
            category=cls.category,
            name="Archived camera",
            description="Fictional archived camera.",
            is_archived=True,
        )
        archive_category(cls.admin.pk, cls.category.pk)
        archive_catalog_item(cls.admin.pk, cls.item.pk)

    def setUp(self) -> None:
        self.client.force_login(self.admin)

    def test_category_restore_preserves_individual_archives_and_history(self) -> None:
        self.client = Client(enforce_csrf_checks=True)
        self.client.force_login(self.admin)
        url: str = reverse("inventory_manage:category-restore", args=[self.category.pk])
        before: int = AuditLog.objects.count()
        confirmation = self.client.get(url)
        self.assertEqual(confirmation.status_code, 200)
        self.category.refresh_from_db()
        self.assertTrue(self.category.is_archived)
        self.assertEqual(AuditLog.objects.count(), before)
        response = self.client.post(
            url,
            {
                "csrfmiddlewaretoken": self.client.cookies["csrftoken"].value,
                "actor_id": self.inactive_admin.pk,
                "name": "Forged",
            },
        )
        self.assertRedirects(
            response, reverse("inventory_manage:category-detail", args=[self.category.pk])
        )
        self.category.refresh_from_db()
        self.item.refresh_from_db()
        self.archived_sibling.refresh_from_db()
        self.assertFalse(self.category.is_archived)
        self.assertEqual(self.category.name, "Test cameras")
        self.assertTrue(self.item.is_archived)
        self.assertTrue(self.archived_sibling.is_archived)
        audit: AuditLog = AuditLog.objects.get(
            action=AuditAction.CATEGORY_RESTORED, target_id=self.category.pk
        )
        self.assertEqual(audit.actor_id, self.admin.pk)
        self.assertEqual(audit.target_model, AuditTarget.CATEGORY)
        self.assertEqual(AuditLog.objects.count(), before + 1)
        self.assertEqual(
            self.client.post(
                url, {"csrfmiddlewaretoken": self.client.cookies["csrftoken"].value}
            ).status_code,
            409,
        )
        self.assertEqual(AuditLog.objects.count(), before + 1)

    def test_item_restore_under_archived_category_preserves_units_photo_and_loan(self) -> None:
        EquipmentUnit.objects.create(
            catalog_item=self.item,
            asset_code="RESTORE-RETIRED-001",
            condition=self.records.catalog.unit.condition,
            acquired_on=self.records.catalog.unit.acquired_on,
            status=UnitStatus.RETIRED,
        )
        CatalogItem.objects.filter(pk=self.item.pk).update(photo="equipment/preserved.webp")
        units_before: tuple[tuple[int, str], ...] = tuple(
            self.item.units.order_by("pk").values_list("pk", "status")
        )
        url: str = reverse("inventory_manage:item-restore", args=[self.item.pk])
        confirmation = self.client.get(url)
        self.assertEqual(confirmation.status_code, 200)
        self.assertContains(confirmation, 'data-testid="restore-category-warning"')
        self.item.refresh_from_db()
        self.assertTrue(self.item.is_archived)
        response = self.client.post(
            url,
            {
                "actor_id": self.inactive_admin.pk,
                "category": "999999",
                "photo": "forged.webp",
                "status": UnitStatus.AVAILABLE,
                "is_archived": "true",
            },
        )
        self.assertRedirects(response, reverse("inventory_manage:item-detail", args=[self.item.pk]))
        self.item.refresh_from_db()
        self.category.refresh_from_db()
        self.assertFalse(self.item.is_archived)
        self.assertTrue(self.category.is_archived)
        self.assertEqual(self.item.category_id, self.category.pk)
        self.assertEqual(self.item.photo.name, "equipment/preserved.webp")
        self.assertEqual(
            tuple(self.item.units.order_by("pk").values_list("pk", "status")), units_before
        )
        self.records.request_item.refresh_from_db()
        self.records.loan.refresh_from_db()
        self.records.loan_unit.refresh_from_db()
        self.records.allocation.refresh_from_db()
        self.assertEqual(self.records.request_item.catalog_item_id, self.item.pk)
        self.assertEqual(self.records.loan.request_id, self.records.request.pk)
        self.assertEqual(self.records.loan_unit.allocation_id, self.records.allocation.pk)
        self.assertIsNone(self.records.allocation.ended_at)
        audit: AuditLog = AuditLog.objects.get(
            action=AuditAction.ITEM_RESTORED, target_id=self.item.pk
        )
        self.assertEqual(audit.actor_id, self.admin.pk)
        self.assertEqual(audit.target_model, AuditTarget.CATALOG_ITEM)
        self.assertEqual(self.client.post(url).status_code, 409)
        self.assertEqual(AuditLog.objects.filter(action=AuditAction.ITEM_RESTORED).count(), 1)

    def test_restoring_category_reactivates_only_items_without_individual_archive(self) -> None:
        restore_catalog_item(self.admin.pk, self.item.pk)
        restore_category(self.admin.pk, self.category.pk)
        self.assertTrue(
            CatalogItem.objects.filter(
                pk=self.item.pk, is_archived=False, category__is_archived=False
            ).exists()
        )
        self.archived_sibling.refresh_from_db()
        self.assertTrue(self.archived_sibling.is_archived)
        for action in (AuditAction.CATEGORY_RESTORED, AuditAction.ITEM_RESTORED):
            response = self.client.get(reverse("operations:audit-list"), {"action": action})
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.context["page"].paginator.count, 1)
            self.assertEqual(response.context["page"].object_list[0].action, action)

    def test_restore_http_access_csrf_methods_and_missing_records(self) -> None:
        before: int = AuditLog.objects.count()
        for route, identifier in (
            ("inventory_manage:category-restore", self.category.pk),
            ("inventory_manage:item-restore", self.item.pk),
        ):
            url: str = reverse(route, args=[identifier])
            with self.subTest(route=route):
                self.client.logout()
                self.assertEqual(self.client.get(url).status_code, 302)
                self.assertEqual(self.client.post(url).status_code, 302)
                for actor in (self.records.catalog.borrower, self.inactive_admin):
                    self.client.force_login(actor)
                    self.assertEqual(self.client.get(url).status_code, 403)
                    self.client.force_login(actor)
                    self.assertEqual(self.client.post(url).status_code, 403)
                self.client.force_login(self.admin)
                csrf_client: Client = Client(enforce_csrf_checks=True)
                csrf_client.force_login(self.admin)
                self.assertEqual(csrf_client.post(url).status_code, 403)
                confirmation = csrf_client.get(url)
                self.assertEqual(confirmation.status_code, 200)
                self.assertEqual(self.client.put(url).status_code, 405)
                self.assertEqual(self.client.delete(url).status_code, 405)
                self.assertEqual(self.client.get(reverse(route, args=[999999])).status_code, 404)
                self.assertEqual(self.client.post(reverse(route, args=[999999])).status_code, 404)
        self.assertEqual(AuditLog.objects.count(), before)

    def test_restore_services_recheck_active_admin(self) -> None:
        before: int = AuditLog.objects.count()
        User.objects.filter(pk=self.admin.pk).update(is_active=False)
        for actor in (self.admin, self.records.catalog.borrower, self.inactive_admin):
            with self.subTest(actor=actor.pk):
                with self.assertRaises(PermissionDenied):
                    restore_category(actor.pk, self.category.pk)
                with self.assertRaises(PermissionDenied):
                    restore_catalog_item(actor.pk, self.item.pk)
        self.category.refresh_from_db()
        self.item.refresh_from_db()
        self.assertTrue(self.category.is_archived)
        self.assertTrue(self.item.is_archived)
        self.assertEqual(AuditLog.objects.count(), before)

    def test_audit_failure_rolls_back_both_restore_actions(self) -> None:
        before: int = AuditLog.objects.count()
        with connection.cursor() as cursor:
            cursor.execute("SET CONSTRAINTS ALL IMMEDIATE")
            cursor.execute(
                "ALTER TABLE operations_auditlog ADD CONSTRAINT test_reject_restore_audit "
                "CHECK (action NOT IN ('CATEGORY_RESTORED', 'ITEM_RESTORED'))"
            )
        with self.assertRaises(IntegrityError):
            restore_category(self.admin.pk, self.category.pk)
        with self.assertRaises(IntegrityError):
            restore_catalog_item(self.admin.pk, self.item.pk)
        self.category.refresh_from_db()
        self.item.refresh_from_db()
        self.assertTrue(self.category.is_archived)
        self.assertTrue(self.item.is_archived)
        self.assertEqual(AuditLog.objects.count(), before)
