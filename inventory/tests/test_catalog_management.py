"""T07 category and catalog item management integration checks."""

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from accounts.models import Profile, User, UserRole
from inventory.models import CatalogItem, Category, EquipmentUnit, UnitCondition, UnitStatus
from inventory.queries import get_item_inventory_counts, has_transactional_history
from operations.models import AuditAction, AuditLog, AuditTarget
from operations.tests.records import create_catalog_records, create_request


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


class CatalogManagementTests(TestCase):
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
        cls.category_laptops: Category = Category.objects.create(
            name="Laptops",
            description="High-performance laptops for coursework.",
            is_archived=False,
        )
        cls.category_archived: Category = Category.objects.create(
            name="Legacy Projectors",
            description="Deprecated overhead projectors.",
            is_archived=True,
        )

        cls.item_camera: CatalogItem = CatalogItem.objects.create(
            category=cls.category_cameras,
            name="Canon EOS 90D",
            description="32.5MP DSLR camera with 18-135mm lens kit.",
            is_archived=False,
        )
        cls.item_laptop: CatalogItem = CatalogItem.objects.create(
            category=cls.category_laptops,
            name="ThinkPad T14",
            description="Core i7 16GB RAM laptop.",
            is_archived=False,
        )
        cls.item_archived: CatalogItem = CatalogItem.objects.create(
            category=cls.category_cameras,
            name="Old Camcorder",
            description="Vintage tape camcorder.",
            is_archived=True,
        )

    def setUp(self) -> None:
        self.client.force_login(self.admin)

    # -------------------------------------------------------------------------
    # Access control tests
    # -------------------------------------------------------------------------
    def test_anonymous_access_redirects_to_login(self) -> None:
        self.client.logout()
        protected_urls: list[str] = [
            reverse("inventory_manage:category-list"),
            reverse("inventory_manage:category-create"),
            reverse("inventory_manage:category-detail", args=[self.category_cameras.pk]),
            reverse("inventory_manage:category-update", args=[self.category_cameras.pk]),
            reverse("inventory_manage:category-archive", args=[self.category_cameras.pk]),
            reverse("inventory_manage:item-list"),
            reverse("inventory_manage:item-create"),
            reverse("inventory_manage:item-detail", args=[self.item_camera.pk]),
            reverse("inventory_manage:item-update", args=[self.item_camera.pk]),
            reverse("inventory_manage:item-archive", args=[self.item_camera.pk]),
        ]
        login_url: str = reverse("accounts:login")
        for url in protected_urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertRedirects(response, f"{login_url}?next={url}")

    def test_basic_user_access_is_forbidden(self) -> None:
        self.client.force_login(self.borrower)
        protected_urls: list[str] = [
            reverse("inventory_manage:category-list"),
            reverse("inventory_manage:category-create"),
            reverse("inventory_manage:category-detail", args=[self.category_cameras.pk]),
            reverse("inventory_manage:category-update", args=[self.category_cameras.pk]),
            reverse("inventory_manage:category-archive", args=[self.category_cameras.pk]),
            reverse("inventory_manage:item-list"),
            reverse("inventory_manage:item-create"),
            reverse("inventory_manage:item-detail", args=[self.item_camera.pk]),
            reverse("inventory_manage:item-update", args=[self.item_camera.pk]),
            reverse("inventory_manage:item-archive", args=[self.item_camera.pk]),
        ]
        for url in protected_urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, 403)

    def test_inactive_admin_access_is_denied(self) -> None:
        self.client.force_login(self.inactive_admin)
        response = self.client.get(reverse("inventory_manage:category-list"))
        self.assertEqual(response.status_code, 403)

    # -------------------------------------------------------------------------
    # Category Management tests
    # -------------------------------------------------------------------------
    def test_category_list_search_and_filter(self) -> None:
        url: str = reverse("inventory_manage:category-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "DSLR Cameras")
        self.assertContains(response, "Laptops")
        self.assertContains(response, "Legacy Projectors")

        # Search by query
        search_response = self.client.get(url, {"q": "DSLR"})
        self.assertEqual(search_response.status_code, 200)
        self.assertContains(search_response, "DSLR Cameras")
        self.assertNotContains(search_response, "Laptops")

        # Filter by active only
        active_response = self.client.get(url, {"archived": "false"})
        self.assertEqual(active_response.status_code, 200)
        self.assertContains(active_response, "DSLR Cameras")
        self.assertNotContains(active_response, "Legacy Projectors")

        # Filter by archived only
        archived_response = self.client.get(url, {"archived": "true"})
        self.assertEqual(archived_response.status_code, 200)
        self.assertContains(archived_response, "Legacy Projectors")
        self.assertNotContains(archived_response, "DSLR Cameras")

    def test_category_list_pagination_and_invalid_page(self) -> None:
        for idx in range(25):
            Category.objects.create(name=f"Extra Category {idx:02d}", description="")
        url: str = reverse("inventory_manage:category-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["page"].object_list), 25)

        # Invalid page 404
        bad_page = self.client.get(url, {"page": "999"})
        self.assertEqual(bad_page.status_code, 404)

    def test_category_create_success_and_audit(self) -> None:
        url: str = reverse("inventory_manage:category-create")
        get_response = self.client.get(url)
        self.assertEqual(get_response.status_code, 200)

        post_data = {"name": "Audio Gear", "description": "Microphones and audio recorders."}
        response = self.client.post(url, post_data)
        new_category = Category.objects.get(name="Audio Gear")
        self.assertRedirects(
            response, reverse("inventory_manage:category-detail", args=[new_category.pk])
        )
        self.assertEqual(new_category.description, "Microphones and audio recorders.")
        self.assertFalse(new_category.is_archived)

        # Verify audit record
        audit: AuditLog = AuditLog.objects.filter(
            action=AuditAction.CATEGORY_CREATED, target_id=new_category.pk
        ).get()
        self.assertEqual(audit.actor_id, self.admin.pk)
        self.assertEqual(audit.target_model, AuditTarget.CATEGORY)
        self.assertIn("Audio Gear", audit.summary)

    def test_category_create_validation_rejections(self) -> None:
        url: str = reverse("inventory_manage:category-create")
        # Blank name
        response = self.client.post(url, {"name": "   ", "description": "Some description"})
        self.assertEqual(response.status_code, 200)
        self.assertIn("name", response.context["form"].errors)
        self.assertIn("Category name cannot be blank.", response.context["form"].errors["name"])

        # Duplicate name (case-insensitive)
        response_dup = self.client.post(
            url, {"name": "dslr cameras", "description": "Duplicate camera category."}
        )
        self.assertEqual(response_dup.status_code, 200)
        self.assertIn("name", response_dup.context["form"].errors)
        self.assertIn(
            "A category with this name already exists.", response_dup.context["form"].errors["name"]
        )

    def test_category_update_success_and_audit(self) -> None:
        url: str = reverse("inventory_manage:category-update", args=[self.category_cameras.pk])
        get_response = self.client.get(url)
        self.assertEqual(get_response.status_code, 200)
        self.assertEqual(get_response.context["form"].initial["name"], "DSLR Cameras")

        response = self.client.post(
            url, {"name": "Still & Video Cameras", "description": "Updated camera description."}
        )
        self.assertRedirects(
            response, reverse("inventory_manage:category-detail", args=[self.category_cameras.pk])
        )
        self.category_cameras.refresh_from_db()
        self.assertEqual(self.category_cameras.name, "Still & Video Cameras")
        self.assertEqual(self.category_cameras.description, "Updated camera description.")

        audit: AuditLog = AuditLog.objects.filter(
            action=AuditAction.CATEGORY_UPDATED, target_id=self.category_cameras.pk
        ).get()
        self.assertEqual(audit.actor_id, self.admin.pk)
        self.assertIn("Still & Video Cameras", audit.summary)

    def test_category_update_duplicate_name_rejection(self) -> None:
        url: str = reverse("inventory_manage:category-update", args=[self.category_cameras.pk])
        response = self.client.post(url, {"name": "laptops", "description": "Conflicting name."})
        self.assertEqual(response.status_code, 200)
        self.assertIn("name", response.context["form"].errors)
        self.assertIn(
            "A category with this name already exists.", response.context["form"].errors["name"]
        )

    def test_category_archive_success_and_conflict(self) -> None:
        url: str = reverse("inventory_manage:category-archive", args=[self.category_laptops.pk])
        get_response = self.client.get(url)
        self.assertEqual(get_response.status_code, 200)
        self.assertContains(get_response, "Archive Laptops?")

        # Confirm archive
        response = self.client.post(url)
        self.assertRedirects(
            response, reverse("inventory_manage:category-detail", args=[self.category_laptops.pk])
        )
        self.category_laptops.refresh_from_db()
        self.assertTrue(self.category_laptops.is_archived)

        audit: AuditLog = AuditLog.objects.filter(
            action=AuditAction.CATEGORY_ARCHIVED, target_id=self.category_laptops.pk
        ).get()
        self.assertEqual(audit.actor_id, self.admin.pk)

        # Repeated archive attempts produce 409 conflict
        conflict_response = self.client.post(url)
        self.assertEqual(conflict_response.status_code, 409)
        self.assertContains(conflict_response, "already archived", status_code=409)

    def test_category_detail_view(self) -> None:
        url: str = reverse("inventory_manage:category-detail", args=[self.category_cameras.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.category_cameras.name)
        self.assertContains(response, "Canon EOS 90D")
        self.assertContains(response, "Old Camcorder")

    # -------------------------------------------------------------------------
    # CatalogItem Management tests
    # -------------------------------------------------------------------------
    def test_item_list_search_and_filters(self) -> None:
        url: str = reverse("inventory_manage:item-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Canon EOS 90D")
        self.assertContains(response, "ThinkPad T14")

        # Search by query
        search_res = self.client.get(url, {"q": "ThinkPad"})
        self.assertEqual(search_res.status_code, 200)
        self.assertContains(search_res, "ThinkPad T14")
        self.assertNotContains(search_res, "Canon EOS 90D")

        # Filter by category
        cat_res = self.client.get(url, {"category": self.category_cameras.pk})
        self.assertEqual(cat_res.status_code, 200)
        self.assertContains(cat_res, "Canon EOS 90D")
        self.assertNotContains(cat_res, "ThinkPad T14")

        # Filter by archived status
        archived_res = self.client.get(url, {"archived": "true"})
        self.assertEqual(archived_res.status_code, 200)
        self.assertContains(archived_res, "Old Camcorder")
        self.assertNotContains(archived_res, "Canon EOS 90D")

    def test_item_create_success_and_audit(self) -> None:
        url: str = reverse("inventory_manage:item-create")
        get_response = self.client.get(url, {"category": self.category_cameras.pk})
        self.assertEqual(get_response.status_code, 200)
        self.assertEqual(
            get_response.context["form"].initial.get("category"), str(self.category_cameras.pk)
        )

        post_data = {
            "category": self.category_cameras.pk,
            "name": "Nikon Z6 II",
            "description": "Full-frame mirrorless camera for studio and field use.",
        }
        response = self.client.post(url, post_data)
        new_item = CatalogItem.objects.get(name="Nikon Z6 II")
        self.assertRedirects(response, reverse("inventory_manage:item-detail", args=[new_item.pk]))
        self.assertEqual(new_item.category, self.category_cameras)
        self.assertFalse(new_item.is_archived)

        audit: AuditLog = AuditLog.objects.filter(
            action=AuditAction.ITEM_CREATED, target_id=new_item.pk
        ).get()
        self.assertEqual(audit.actor_id, self.admin.pk)
        self.assertIn("Nikon Z6 II", audit.summary)

    def test_item_create_under_archived_category_rejected(self) -> None:
        url: str = reverse("inventory_manage:item-create")
        post_data = {
            "category": self.category_archived.pk,
            "name": "Kodak Carousel",
            "description": "Slide projector.",
        }
        response = self.client.post(url, post_data)
        self.assertEqual(response.status_code, 200)
        self.assertIn("category", response.context["form"].errors)
        self.assertIn("Select a valid choice", response.context["form"].errors["category"][0])

    def test_item_update_category_allowed_before_transactional_history(self) -> None:
        url: str = reverse("inventory_manage:item-update", args=[self.item_laptop.pk])
        self.assertFalse(has_transactional_history(self.item_laptop.pk))

        # Can change category from Laptops to Cameras before history exists
        response = self.client.post(
            url,
            {
                "category": self.category_cameras.pk,
                "name": "ThinkPad T14 (Camera Station)",
                "description": "Laptop configured for video ingest.",
            },
        )
        self.assertRedirects(
            response, reverse("inventory_manage:item-detail", args=[self.item_laptop.pk])
        )
        self.item_laptop.refresh_from_db()
        self.assertEqual(self.item_laptop.category, self.category_cameras)
        self.assertEqual(self.item_laptop.name, "ThinkPad T14 (Camera Station)")

        audit: AuditLog = AuditLog.objects.filter(
            action=AuditAction.ITEM_UPDATED, target_id=self.item_laptop.pk
        ).get()
        self.assertEqual(audit.actor_id, self.admin.pk)

    def test_item_update_category_locked_after_transactional_history(self) -> None:
        # Create a unit under item_camera, establishing transactional history
        EquipmentUnit.objects.create(
            catalog_item=self.item_camera,
            asset_code="CAM-HIST-01",
            condition=UnitCondition.GOOD,
            acquired_on=timezone.localdate(),
            status=UnitStatus.AVAILABLE,
            internal_notes="",
        )
        self.assertTrue(has_transactional_history(self.item_camera.pk))

        url: str = reverse("inventory_manage:item-update", args=[self.item_camera.pk])
        get_response = self.client.get(url)
        self.assertTrue(get_response.context["has_history"])
        self.assertTrue(get_response.context["form"].fields["category"].disabled)

        # Attempt to change category via POST
        post_response = self.client.post(
            url,
            {
                "category": self.category_laptops.pk,
                "name": "Canon EOS 90D Updated",
                "description": "Updated description with unchanged category.",
            },
        )
        self.assertRedirects(
            post_response, reverse("inventory_manage:item-detail", args=[self.item_camera.pk])
        )
        self.item_camera.refresh_from_db()
        # Category must remain unchanged
        self.assertEqual(self.item_camera.category, self.category_cameras)
        self.assertEqual(self.item_camera.name, "Canon EOS 90D Updated")

    def test_item_update_category_locked_after_request_item_history(self) -> None:
        # Create a request item referencing item_laptop
        catalog = create_catalog_records()
        create_request(catalog.borrower.pk, self.item_laptop.pk, timezone.now())
        self.assertTrue(has_transactional_history(self.item_laptop.pk))

        url: str = reverse("inventory_manage:item-update", args=[self.item_laptop.pk])
        get_response = self.client.get(url)
        self.assertTrue(get_response.context["has_history"])

    def test_item_archive_success_and_conflict(self) -> None:
        url: str = reverse("inventory_manage:item-archive", args=[self.item_laptop.pk])
        get_response = self.client.get(url)
        self.assertEqual(get_response.status_code, 200)
        self.assertContains(get_response, "Archive ThinkPad T14?")

        response = self.client.post(url)
        self.assertRedirects(
            response, reverse("inventory_manage:item-detail", args=[self.item_laptop.pk])
        )
        self.item_laptop.refresh_from_db()
        self.assertTrue(self.item_laptop.is_archived)

        audit: AuditLog = AuditLog.objects.filter(
            action=AuditAction.ITEM_ARCHIVED, target_id=self.item_laptop.pk
        ).get()
        self.assertEqual(audit.actor_id, self.admin.pk)

        # Conflict on repeat
        conflict_res = self.client.post(url)
        self.assertEqual(conflict_res.status_code, 409)
        self.assertContains(conflict_res, "already archived", status_code=409)

    def test_item_detail_derived_inventory_counts(self) -> None:
        # Create units in all 5 statuses
        today = timezone.localdate()
        EquipmentUnit.objects.create(
            catalog_item=self.item_camera,
            asset_code="CAM-UNIT-01",
            condition=UnitCondition.GOOD,
            acquired_on=today,
            status=UnitStatus.AVAILABLE,
        )
        EquipmentUnit.objects.create(
            catalog_item=self.item_camera,
            asset_code="CAM-UNIT-02",
            condition=UnitCondition.GOOD,
            acquired_on=today,
            status=UnitStatus.RESERVED,
        )
        EquipmentUnit.objects.create(
            catalog_item=self.item_camera,
            asset_code="CAM-UNIT-03",
            condition=UnitCondition.FAIR,
            acquired_on=today,
            status=UnitStatus.ISSUED,
        )
        EquipmentUnit.objects.create(
            catalog_item=self.item_camera,
            asset_code="CAM-UNIT-04",
            condition=UnitCondition.DAMAGED,
            acquired_on=today,
            status=UnitStatus.MAINTENANCE,
        )
        EquipmentUnit.objects.create(
            catalog_item=self.item_camera,
            asset_code="CAM-UNIT-05",
            condition=UnitCondition.DAMAGED,
            acquired_on=today,
            status=UnitStatus.RETIRED,
        )

        counts = get_item_inventory_counts(self.item_camera.pk)
        self.assertEqual(counts.available, 1)
        self.assertEqual(counts.reserved, 1)
        self.assertEqual(counts.issued, 1)
        self.assertEqual(counts.maintenance, 1)
        self.assertEqual(counts.retired, 1)
        # BR-12: Serviceable = Available + Reserved + Issued = 3
        self.assertEqual(counts.serviceable, 3)
        # Total = 5
        self.assertEqual(counts.total, 5)

        url: str = reverse("inventory_manage:item-detail", args=[self.item_camera.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["counts"].serviceable, 3)
        self.assertEqual(response.context["counts"].total, 5)
        self.assertContains(response, 'data-testid="count-serviceable"')
        self.assertContains(response, 'data-testid="count-total"')
        self.assertContains(response, "CAM-UNIT-01")
        self.assertContains(response, "CAM-UNIT-05")

    def test_pending_unit_and_maintenance_placeholders_preserved(self) -> None:
        unit_url: str = reverse("inventory_manage:unit-list")
        unit_res = self.client.get(unit_url)
        self.assertEqual(unit_res.status_code, 200)
        self.assertContains(unit_res, "T08 · Kenneth")

        maint_url: str = reverse("inventory_manage:maintenance-list")
        maint_res = self.client.get(maint_url)
        self.assertEqual(maint_res.status_code, 200)
        self.assertContains(maint_res, "T16 · Kenneth")
