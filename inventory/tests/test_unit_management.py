"""T08 physical unit management integration checks."""

from datetime import timedelta

from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from accounts.models import Profile, User, UserRole
from borrowing.models import (
    BorrowRequest,
    RequestItem,
    RequestStatus,
    UnitAllocation,
)
from inventory.models import (
    CatalogItem,
    Category,
    EquipmentUnit,
    MaintenanceRecord,
    MaintenanceStatus,
    UnitCondition,
    UnitStatus,
)
from inventory.queries import (
    get_overall_inventory_counts,
    has_unit_transactional_history,
    list_equipment_units,
)
from inventory.services import create_equipment_unit, update_equipment_unit
from operations.models import AuditAction, AuditLog, AuditTarget


def create_user(username: str, role: UserRole, is_active: bool) -> User:
    """Create a test user with a Profile required by the application contract."""
    user: User = User.objects.create_user(
        username=username,
        email=f"{username}@example.invalid",
        password=None,
        first_name="Fictional",
        last_name="TestUser",
        role=role,
        is_active=is_active,
    )
    Profile.objects.create(user=user, contact_number="")
    return user


class PhysicalUnitManagementTests(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.admin: User = create_user("admin_kenneth", UserRole.ADMIN, True)
        cls.borrower: User = create_user("borrower_kenneth", UserRole.BASIC_USER, True)
        cls.inactive_admin: User = create_user("inactive_admin_k", UserRole.ADMIN, False)

        cls.category_cameras: Category = Category.objects.create(
            name="DSLR Cameras",
            description="Professional cameras and lenses.",
            is_archived=False,
        )
        cls.category_audio: Category = Category.objects.create(
            name="Audio Equipment",
            description="Microphones and mixers.",
            is_archived=False,
        )
        cls.category_archived: Category = Category.objects.create(
            name="Obsolete Hardware",
            description="Archived hardware category.",
            is_archived=True,
        )

        cls.item_camera: CatalogItem = CatalogItem.objects.create(
            category=cls.category_cameras,
            name="Canon EOS 90D",
            description="Mid-range DSLR camera body.",
            is_archived=False,
        )
        cls.item_mic: CatalogItem = CatalogItem.objects.create(
            category=cls.category_audio,
            name="Rode Wireless GO II",
            description="Wireless dual microphone system.",
            is_archived=False,
        )
        cls.item_archived: CatalogItem = CatalogItem.objects.create(
            category=cls.category_cameras,
            name="Canon Rebel T3",
            description="Legacy DSLR camera.",
            is_archived=True,
        )
        cls.item_in_archived_category: CatalogItem = CatalogItem.objects.create(
            category=cls.category_archived,
            name="Zip Drive 100",
            description="Old magnetic storage drive.",
            is_archived=False,
        )

        cls.unit_available: EquipmentUnit = EquipmentUnit.objects.create(
            catalog_item=cls.item_camera,
            asset_code="CAM-90D-001",
            condition=UnitCondition.GOOD,
            acquired_on=timezone.localdate() - timedelta(days=30),
            status=UnitStatus.AVAILABLE,
            internal_notes="Unit in primary inventory.",
        )

    def setUp(self) -> None:
        self.admin_client: Client = Client()
        self.admin_client.force_login(self.admin)

        self.borrower_client: Client = Client()
        self.borrower_client.force_login(self.borrower)

        self.inactive_client: Client = Client()
        self.inactive_client.force_login(self.inactive_admin)

        self.anonymous_client: Client = Client()

    # -------------------------------------------------------------------------
    # Access and Authorization Controls
    # -------------------------------------------------------------------------

    def test_anonymous_redirected_to_login(self) -> None:
        for url in [
            reverse("inventory_manage:unit-list"),
            reverse("inventory_manage:unit-create"),
            reverse("inventory_manage:unit-detail", kwargs={"unit_id": self.unit_available.pk}),
            reverse("inventory_manage:unit-update", kwargs={"unit_id": self.unit_available.pk}),
        ]:
            response = self.anonymous_client.get(url)
            self.assertEqual(response.status_code, 302)
            self.assertIn("/accounts/login/", response.headers["Location"])

    def test_basic_user_denied_access(self) -> None:
        for url in [
            reverse("inventory_manage:unit-list"),
            reverse("inventory_manage:unit-create"),
            reverse("inventory_manage:unit-detail", kwargs={"unit_id": self.unit_available.pk}),
            reverse("inventory_manage:unit-update", kwargs={"unit_id": self.unit_available.pk}),
        ]:
            response = self.borrower_client.get(url)
            self.assertIn(response.status_code, [302, 403])

    def test_inactive_admin_denied_access(self) -> None:
        for url in [
            reverse("inventory_manage:unit-list"),
            reverse("inventory_manage:unit-create"),
            reverse("inventory_manage:unit-detail", kwargs={"unit_id": self.unit_available.pk}),
            reverse("inventory_manage:unit-update", kwargs={"unit_id": self.unit_available.pk}),
        ]:
            client = Client()
            client.force_login(self.inactive_admin)
            response = client.get(url)
            self.assertEqual(response.status_code, 403)

    def test_active_admin_granted_access(self) -> None:
        for url in [
            reverse("inventory_manage:unit-list"),
            reverse("inventory_manage:unit-create"),
            reverse("inventory_manage:unit-detail", kwargs={"unit_id": self.unit_available.pk}),
            reverse("inventory_manage:unit-update", kwargs={"unit_id": self.unit_available.pk}),
        ]:
            response = self.admin_client.get(url)
            self.assertEqual(response.status_code, 200)

    # -------------------------------------------------------------------------
    # Unit Registration / Creation
    # -------------------------------------------------------------------------

    def test_create_good_unit_becomes_available_with_audit(self) -> None:
        unit: EquipmentUnit = create_equipment_unit(
            actor_id=self.admin.pk,
            catalog_item_id=self.item_camera.pk,
            asset_code="CAM-90D-002",
            condition=UnitCondition.GOOD,
            acquired_on=timezone.localdate(),
            internal_notes="Purchased brand new.",
            maintenance_problem=None,
        )
        self.assertEqual(unit.status, UnitStatus.AVAILABLE)
        self.assertEqual(unit.condition, UnitCondition.GOOD)
        self.assertEqual(unit.asset_code, "CAM-90D-002")

        # Verify audit log
        audit = AuditLog.objects.filter(
            action=AuditAction.UNIT_CREATED,
            target_model=AuditTarget.EQUIPMENT_UNIT,
            target_id=unit.pk,
        ).first()
        self.assertIsNotNone(audit)
        self.assertEqual(audit.actor, self.admin)
        self.assertIn("CAM-90D-002", audit.summary)

        # No maintenance opened
        self.assertFalse(MaintenanceRecord.objects.filter(unit=unit).exists())

    def test_create_fair_unit_becomes_available(self) -> None:
        unit: EquipmentUnit = create_equipment_unit(
            actor_id=self.admin.pk,
            catalog_item_id=self.item_mic.pk,
            asset_code="MIC-RODE-001",
            condition=UnitCondition.FAIR,
            acquired_on=timezone.localdate(),
            internal_notes="Minor cosmetic scratches.",
            maintenance_problem=None,
        )
        self.assertEqual(unit.status, UnitStatus.AVAILABLE)
        self.assertEqual(unit.condition, UnitCondition.FAIR)

    def test_create_damaged_unit_creates_maintenance_and_two_audits(self) -> None:
        unit: EquipmentUnit = create_equipment_unit(
            actor_id=self.admin.pk,
            catalog_item_id=self.item_camera.pk,
            asset_code="CAM-90D-003",
            condition=UnitCondition.DAMAGED,
            acquired_on=timezone.localdate(),
            internal_notes="Arrived with broken hotshoe.",
            maintenance_problem="Broken hotshoe mount requiring replacement.",
        )
        self.assertEqual(unit.status, UnitStatus.MAINTENANCE)
        self.assertEqual(unit.condition, UnitCondition.DAMAGED)

        # Maintenance record verified
        maint = MaintenanceRecord.objects.filter(unit=unit).first()
        self.assertIsNotNone(maint)
        self.assertEqual(maint.status, MaintenanceStatus.OPEN)
        self.assertEqual(maint.problem, "Broken hotshoe mount requiring replacement.")
        self.assertEqual(maint.opened_by, self.admin)
        self.assertIsNone(maint.source_return)

        # Two audits: UNIT_CREATED and MAINTENANCE_OPENED
        unit_audit = AuditLog.objects.filter(
            action=AuditAction.UNIT_CREATED, target_id=unit.pk
        ).first()
        self.assertIsNotNone(unit_audit)

        maint_audit = AuditLog.objects.filter(
            action=AuditAction.MAINTENANCE_OPENED, target_id=maint.pk
        ).first()
        self.assertIsNotNone(maint_audit)
        self.assertIn("CAM-90D-003", maint_audit.summary)

    def test_create_damaged_unit_without_problem_fails(self) -> None:
        with self.assertRaises(ValidationError):
            create_equipment_unit(
                actor_id=self.admin.pk,
                catalog_item_id=self.item_camera.pk,
                asset_code="CAM-90D-004",
                condition=UnitCondition.DAMAGED,
                acquired_on=timezone.localdate(),
                internal_notes="Damaged.",
                maintenance_problem="",
            )
        self.assertFalse(EquipmentUnit.objects.filter(asset_code="CAM-90D-004").exists())

    def test_duplicate_asset_code_case_insensitive_rejected(self) -> None:
        with self.assertRaises(ValidationError):
            create_equipment_unit(
                actor_id=self.admin.pk,
                catalog_item_id=self.item_camera.pk,
                asset_code="cam-90d-001",  # Same as self.unit_available.asset_code
                condition=UnitCondition.GOOD,
                acquired_on=timezone.localdate(),
                internal_notes="",
                maintenance_problem=None,
            )

    def test_future_acquisition_date_rejected(self) -> None:
        future_date = timezone.localdate() + timedelta(days=1)
        with self.assertRaises(ValidationError):
            create_equipment_unit(
                actor_id=self.admin.pk,
                catalog_item_id=self.item_camera.pk,
                asset_code="CAM-90D-FUTURE",
                condition=UnitCondition.GOOD,
                acquired_on=future_date,
                internal_notes="",
                maintenance_problem=None,
            )

    def test_create_under_archived_catalog_item_rejected(self) -> None:
        with self.assertRaises(ValidationError):
            create_equipment_unit(
                actor_id=self.admin.pk,
                catalog_item_id=self.item_archived.pk,
                asset_code="CAM-REBEL-001",
                condition=UnitCondition.GOOD,
                acquired_on=timezone.localdate(),
                internal_notes="",
                maintenance_problem=None,
            )

    def test_create_under_archived_category_rejected(self) -> None:
        with self.assertRaises(ValidationError):
            create_equipment_unit(
                actor_id=self.admin.pk,
                catalog_item_id=self.item_in_archived_category.pk,
                asset_code="ZIP-100-001",
                condition=UnitCondition.GOOD,
                acquired_on=timezone.localdate(),
                internal_notes="",
                maintenance_problem=None,
            )

    def test_unit_create_view_post_success(self) -> None:
        response = self.admin_client.post(
            reverse("inventory_manage:unit-create"),
            {
                "catalog_item": self.item_camera.pk,
                "asset_code": "CAM-VIEW-001",
                "condition": UnitCondition.GOOD,
                "acquired_on": timezone.localdate().isoformat(),
                "internal_notes": "Added via web form.",
            },
        )
        unit = EquipmentUnit.objects.filter(asset_code="CAM-VIEW-001").first()
        self.assertIsNotNone(unit)
        self.assertRedirects(
            response, reverse("inventory_manage:unit-detail", kwargs={"unit_id": unit.pk})
        )

    def test_unit_create_view_form_validation_error(self) -> None:
        response = self.admin_client.post(
            reverse("inventory_manage:unit-create"),
            {
                "catalog_item": self.item_camera.pk,
                "asset_code": self.unit_available.asset_code,  # Duplicate!
                "condition": UnitCondition.GOOD,
                "acquired_on": timezone.localdate().isoformat(),
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "A physical unit with this asset code already exists.")

    # -------------------------------------------------------------------------
    # Unit Editing / Updating
    # -------------------------------------------------------------------------

    def test_update_unit_without_history_allows_code_item_date_notes(self) -> None:
        new_date = timezone.localdate() - timedelta(days=10)
        updated = update_equipment_unit(
            actor_id=self.admin.pk,
            unit_id=self.unit_available.pk,
            internal_notes="Updated notes without history.",
            asset_code="CAM-90D-RENAME",
            catalog_item_id=self.item_mic.pk,
            acquired_on=new_date,
        )
        self.assertEqual(updated.asset_code, "CAM-90D-RENAME")
        self.assertEqual(updated.catalog_item_id, self.item_mic.pk)
        self.assertEqual(updated.acquired_on, new_date)
        self.assertEqual(updated.internal_notes, "Updated notes without history.")

        audit = AuditLog.objects.filter(
            action=AuditAction.UNIT_UPDATED,
            target_id=updated.pk,
        ).first()
        self.assertIsNotNone(audit)
        self.assertIn("CAM-90D-RENAME", audit.summary)

    def test_update_unit_with_history_locks_code_item_date(self) -> None:
        # Create an allocation for this unit to establish transactional history
        sub_time = timezone.now() - timedelta(days=2)
        req = BorrowRequest.objects.create(
            owner=self.borrower,
            purpose="Documentary project",
            submitted_at=sub_time,
            submitted_on=timezone.localdate(sub_time),
            desired_due_date=timezone.localdate(sub_time) + timedelta(days=3),
            agreed_due_date=timezone.localdate(sub_time) + timedelta(days=3),
            max_loan_days_applied=7,
            max_quantity_applied=3,
            status=RequestStatus.APPROVED,
            decided_by=self.admin,
            decided_at=sub_time,
            decision_reason="Approved for class project.",
        )
        req_item = RequestItem.objects.create(
            request=req,
            catalog_item=self.unit_available.catalog_item,
            quantity=1,
        )
        UnitAllocation.objects.create(
            request_item=req_item,
            unit=self.unit_available,
            allocated_at=sub_time,
            allocated_by=self.admin,
        )

        self.assertTrue(has_unit_transactional_history(self.unit_available.pk))

        # Attempting to change asset code fails
        with self.assertRaises(ValidationError):
            update_equipment_unit(
                actor_id=self.admin.pk,
                unit_id=self.unit_available.pk,
                internal_notes="Trying to rename.",
                asset_code="NEW-CODE-LOCKED",
                catalog_item_id=self.unit_available.catalog_item_id,
                acquired_on=self.unit_available.acquired_on,
            )

        # Attempting to change catalog item fails
        with self.assertRaises(ValidationError):
            update_equipment_unit(
                actor_id=self.admin.pk,
                unit_id=self.unit_available.pk,
                internal_notes="Trying to reassign item.",
                asset_code=self.unit_available.asset_code,
                catalog_item_id=self.item_mic.pk,
                acquired_on=self.unit_available.acquired_on,
            )

        # Attempting to change acquired_on fails
        with self.assertRaises(ValidationError):
            update_equipment_unit(
                actor_id=self.admin.pk,
                unit_id=self.unit_available.pk,
                internal_notes="Trying to change date.",
                asset_code=self.unit_available.asset_code,
                catalog_item_id=self.unit_available.catalog_item_id,
                acquired_on=timezone.localdate() - timedelta(days=50),
            )

        # Updating internal notes succeeds
        updated = update_equipment_unit(
            actor_id=self.admin.pk,
            unit_id=self.unit_available.pk,
            internal_notes="Updated notes only.",
            asset_code=None,
            catalog_item_id=None,
            acquired_on=None,
        )
        self.assertEqual(updated.internal_notes, "Updated notes only.")
        self.assertEqual(updated.asset_code, self.unit_available.asset_code)

    def test_unit_update_view_post_success(self) -> None:
        response = self.admin_client.post(
            reverse("inventory_manage:unit-update", kwargs={"unit_id": self.unit_available.pk}),
            {
                "catalog_item": self.unit_available.catalog_item_id,
                "asset_code": "CAM-90D-EDITED",
                "acquired_on": self.unit_available.acquired_on.isoformat(),
                "internal_notes": "Edited via view.",
            },
        )
        self.unit_available.refresh_from_db()
        self.assertEqual(self.unit_available.asset_code, "CAM-90D-EDITED")
        self.assertEqual(self.unit_available.internal_notes, "Edited via view.")
        self.assertRedirects(
            response,
            reverse("inventory_manage:unit-detail", kwargs={"unit_id": self.unit_available.pk}),
        )

    # -------------------------------------------------------------------------
    # List, Filtering, and Pagination
    # -------------------------------------------------------------------------

    def test_unit_list_filters(self) -> None:
        # Create additional units with various attributes
        mic_unit = EquipmentUnit.objects.create(
            catalog_item=self.item_mic,
            asset_code="MIC-FILTER-001",
            condition=UnitCondition.GOOD,
            acquired_on=timezone.localdate(),
            status=UnitStatus.AVAILABLE,
        )
        maint_unit = EquipmentUnit.objects.create(
            catalog_item=self.item_camera,
            asset_code="CAM-MAINT-001",
            condition=UnitCondition.DAMAGED,
            acquired_on=timezone.localdate(),
            status=UnitStatus.MAINTENANCE,
        )

        # 1. Search by asset code
        res_q = list_equipment_units("FILTER", None, None, None)
        self.assertEqual(list(res_q), [mic_unit])

        # 2. Filter by category
        res_cat = list_equipment_units("", self.category_audio.pk, None, None)
        self.assertEqual(list(res_cat), [mic_unit])

        # 3. Filter by item
        res_item = list_equipment_units("", None, self.item_camera.pk, None)
        self.assertIn(self.unit_available, res_item)
        self.assertIn(maint_unit, res_item)
        self.assertNotIn(mic_unit, res_item)

        # 4. Filter by status
        res_status = list_equipment_units("", None, None, UnitStatus.MAINTENANCE)
        self.assertEqual(list(res_status), [maint_unit])

    def test_overall_inventory_counts(self) -> None:
        counts = get_overall_inventory_counts()
        self.assertEqual(counts.total, EquipmentUnit.objects.count())
        self.assertEqual(
            counts.available, EquipmentUnit.objects.filter(status=UnitStatus.AVAILABLE).count()
        )
        self.assertEqual(counts.serviceable, counts.available + counts.reserved + counts.issued)

    def test_unit_list_view_renders_cards_and_table(self) -> None:
        response = self.admin_client.get(reverse("inventory_manage:unit-list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Physical units")
        self.assertContains(response, self.unit_available.asset_code)
        self.assertContains(response, 'data-testid="count-available"')
        self.assertContains(response, 'data-testid="count-total"')

    def test_unit_detail_view_renders_unit_and_history(self) -> None:
        # Create an allocation and maintenance record
        sub_time = timezone.now() - timedelta(days=1)
        req = BorrowRequest.objects.create(
            owner=self.borrower,
            purpose="Robotics competition",
            submitted_at=sub_time,
            submitted_on=timezone.localdate(sub_time),
            desired_due_date=timezone.localdate(sub_time) + timedelta(days=2),
            agreed_due_date=timezone.localdate(sub_time) + timedelta(days=2),
            max_loan_days_applied=7,
            max_quantity_applied=3,
            status=RequestStatus.APPROVED,
            decided_by=self.admin,
            decided_at=sub_time,
            decision_reason="Approved",
        )
        req_item = RequestItem.objects.create(
            request=req, catalog_item=self.unit_available.catalog_item, quantity=1
        )
        UnitAllocation.objects.create(
            request_item=req_item,
            unit=self.unit_available,
            allocated_at=sub_time,
            allocated_by=self.admin,
        )
        MaintenanceRecord.objects.create(
            unit=self.unit_available,
            problem="Loose lens mount screw.",
            opened_at=sub_time,
            opened_by=self.admin,
            status=MaintenanceStatus.OPEN,
        )

        response = self.admin_client.get(
            reverse("inventory_manage:unit-detail", kwargs={"unit_id": self.unit_available.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.unit_available.asset_code)
        self.assertContains(response, "Robotics competition")
        self.assertContains(response, "Loose lens mount screw.")
        self.assertContains(response, "Transaction history preserved")

    def test_unit_detail_nonexistent_returns_404(self) -> None:
        response = self.admin_client.get(
            reverse("inventory_manage:unit-detail", kwargs={"unit_id": 999999})
        )
        self.assertEqual(response.status_code, 404)

    # -------------------------------------------------------------------------
    # Database Constraint Integrity
    # -------------------------------------------------------------------------

    def test_db_constraint_damaged_unavailable_enforced(self) -> None:
        with self.assertRaises(IntegrityError):
            EquipmentUnit.objects.create(
                catalog_item=self.item_camera,
                asset_code="DAMAGED-AVAILABLE-FAIL",
                condition=UnitCondition.DAMAGED,
                acquired_on=timezone.localdate(),
                status=UnitStatus.AVAILABLE,  # Violates unit_damaged_unavailable constraint!
            )
