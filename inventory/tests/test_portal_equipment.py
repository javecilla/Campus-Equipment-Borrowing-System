"""Tests for borrower equipment catalog browsing, detail, and confidentiality."""

import io

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone
from PIL import Image

from accounts.models import User
from inventory.models import CatalogItem, Category, EquipmentUnit, UnitCondition, UnitStatus
from operations.tests.records import CatalogRecords, create_catalog_records
from operations.tests.test_navigation import NavigationLinks


def _generate_test_webp() -> bytes:
    buffer = io.BytesIO()
    image = Image.new("RGB", (10, 10), color="green")
    image.save(buffer, format="WEBP")
    return buffer.getvalue()


class PortalEquipmentAccessTests(TestCase):
    records: CatalogRecords

    @classmethod
    def setUpTestData(cls) -> None:
        cls.records = create_catalog_records()

    def test_anonymous_requests_redirect_to_login(self) -> None:
        client = Client()
        list_url = reverse("portal:equipment-list")
        detail_url = reverse("portal:equipment-detail", args=[self.records.item.pk])
        photo_url = reverse("portal:equipment-photo", args=[self.records.item.pk])

        for url in (list_url, detail_url, photo_url):
            with self.subTest(url=url):
                response = client.get(url)
                self.assertRedirects(response, f"{reverse('accounts:login')}?next={url}")

    def test_admin_cannot_access_portal_equipment_views(self) -> None:
        self.client.force_login(self.records.admin)
        for url in (
            reverse("portal:equipment-list"),
            reverse("portal:equipment-detail", args=[self.records.item.pk]),
            reverse("portal:equipment-photo", args=[self.records.item.pk]),
        ):
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 403)

    def test_deactivated_basic_user_receives_403(self) -> None:
        for url in (
            reverse("portal:equipment-list"),
            reverse("portal:equipment-detail", args=[self.records.item.pk]),
            reverse("portal:equipment-photo", args=[self.records.item.pk]),
        ):
            with self.subTest(url=url):
                User.objects.filter(pk=self.records.borrower.pk).update(is_active=True)
                self.records.borrower.refresh_from_db()
                self.client.force_login(self.records.borrower)
                User.objects.filter(pk=self.records.borrower.pk).update(is_active=False)
                self.assertEqual(self.client.get(url).status_code, 403)

    def test_mutating_methods_are_rejected_with_405(self) -> None:
        self.client.force_login(self.records.borrower)
        list_url = reverse("portal:equipment-list")
        detail_url = reverse("portal:equipment-detail", args=[self.records.item.pk])
        photo_url = reverse("portal:equipment-photo", args=[self.records.item.pk])

        for url in (list_url, detail_url, photo_url):
            with self.subTest(url=url):
                self.assertEqual(self.client.post(url, {"data": "test"}).status_code, 405)
                self.assertEqual(self.client.put(url, {"data": "test"}).status_code, 405)
                self.assertEqual(self.client.delete(url).status_code, 405)

    def test_head_requests_succeed_for_basic_user(self) -> None:
        self.client.force_login(self.records.borrower)
        self.assertEqual(self.client.head(reverse("portal:equipment-list")).status_code, 200)
        self.assertEqual(
            self.client.head(
                reverse("portal:equipment-detail", args=[self.records.item.pk])
            ).status_code,
            200,
        )


class PortalEquipmentCatalogSearchTests(TestCase):
    records: CatalogRecords
    cat_audio: Category
    cat_photo: Category
    item_mic: CatalogItem
    item_headphones: CatalogItem
    item_dslr: CatalogItem

    @classmethod
    def setUpTestData(cls) -> None:
        cls.records = create_catalog_records()
        cls.cat_audio = Category.objects.create(
            name="Audio Lab", description="Microphones and mixers"
        )
        cls.cat_photo = Category.objects.create(
            name="Photo Studio", description="Cameras and lights"
        )

        cls.item_mic = CatalogItem.objects.create(
            category=cls.cat_audio,
            name="Condenser Microphone",
            description="Studio microphone with cardioid pickup pattern.",
        )
        cls.item_headphones = CatalogItem.objects.create(
            category=cls.cat_audio,
            name="Monitor Headphones",
            description="Closed-back studio reference headphones.",
        )
        cls.item_dslr = CatalogItem.objects.create(
            category=cls.cat_photo,
            name="DSLR Camera Body",
            description="High-resolution digital camera for field production.",
        )

    def setUp(self) -> None:
        self.client.force_login(self.records.borrower)

    def test_default_list_shows_all_active_items(self) -> None:
        response = self.client.get(reverse("portal:equipment-list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Browse campus equipment")
        self.assertContains(response, self.item_mic.name)
        self.assertContains(response, self.item_headphones.name)
        self.assertContains(response, self.item_dslr.name)

    def test_search_by_item_name(self) -> None:
        response = self.client.get(reverse("portal:equipment-list"), {"q": "Microphone"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.item_mic.name)
        self.assertNotContains(response, self.item_headphones.name)
        self.assertNotContains(response, self.item_dslr.name)

    def test_search_by_description(self) -> None:
        response = self.client.get(reverse("portal:equipment-list"), {"q": "closed-back"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.item_headphones.name)
        self.assertNotContains(response, self.item_mic.name)
        self.assertNotContains(response, self.item_dslr.name)

    def test_filter_by_category(self) -> None:
        response = self.client.get(
            reverse("portal:equipment-list"), {"category": str(self.cat_photo.pk)}
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.item_dslr.name)
        self.assertNotContains(response, self.item_mic.name)
        self.assertNotContains(response, self.item_headphones.name)

    def test_combined_search_and_category_filter(self) -> None:
        response = self.client.get(
            reverse("portal:equipment-list"),
            {"q": "Headphones", "category": str(self.cat_audio.pk)},
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.item_headphones.name)
        self.assertNotContains(response, self.item_mic.name)
        self.assertNotContains(response, self.item_dslr.name)

    def test_empty_results_renders_helpful_empty_state(self) -> None:
        response = self.client.get(reverse("portal:equipment-list"), {"q": "NonexistentWidget"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'data-testid="portal-equipment-empty"')
        self.assertContains(response, "No equipment items found")
        self.assertContains(response, "Clear all filters")

    def test_invalid_category_returns_200_with_empty_results(self) -> None:
        response = self.client.get(reverse("portal:equipment-list"), {"category": "999999"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No equipment items found")

    def test_pagination_at_twenty_five_items(self) -> None:
        category = Category.objects.create(name="Batch Testing", description="")
        items = [
            CatalogItem(
                category=category,
                name=f"Bulk Item {i:02d}",
                description=f"Description for item {i}",
            )
            for i in range(30)
        ]
        CatalogItem.objects.bulk_create(items)

        # Page 1
        page1 = self.client.get(reverse("portal:equipment-list"), {"category": str(category.pk)})
        self.assertEqual(page1.status_code, 200)
        self.assertEqual(len(page1.context["page"]), 25)
        self.assertTrue(page1.context["page"].has_next())

        # Page 2
        page2 = self.client.get(
            reverse("portal:equipment-list"), {"category": str(category.pk), "page": "2"}
        )
        self.assertEqual(page2.status_code, 200)
        self.assertEqual(len(page2.context["page"]), 5)
        self.assertTrue(page2.context["page"].has_previous())

        # Invalid page 404
        page_invalid = self.client.get(
            reverse("portal:equipment-list"), {"category": str(category.pk), "page": "999"}
        )
        self.assertEqual(page_invalid.status_code, 404)


class PortalEquipmentArchivalExclusionTests(TestCase):
    records: CatalogRecords
    archived_category: Category
    item_in_archived_category: CatalogItem
    archived_item: CatalogItem

    @classmethod
    def setUpTestData(cls) -> None:
        cls.records = create_catalog_records()
        cls.archived_category = Category.objects.create(
            name="Retired Department", description="", is_archived=True
        )
        cls.item_in_archived_category = CatalogItem.objects.create(
            category=cls.archived_category,
            name="Deprecated Projector",
            description="Projector under archived category.",
            is_archived=False,
        )
        cls.archived_item = CatalogItem.objects.create(
            category=cls.records.category,
            name="Archived Audio Recorder",
            description="Individually archived recorder.",
            is_archived=True,
        )

    def setUp(self) -> None:
        self.client.force_login(self.records.borrower)

    def test_archived_items_and_items_under_archived_categories_are_excluded_from_list(
        self,
    ) -> None:
        response = self.client.get(reverse("portal:equipment-list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.records.item.name)
        self.assertNotContains(response, self.archived_item.name)
        self.assertNotContains(response, self.item_in_archived_category.name)

    def test_archived_item_detail_returns_404(self) -> None:
        response = self.client.get(reverse("portal:equipment-detail", args=[self.archived_item.pk]))
        self.assertEqual(response.status_code, 404)

    def test_item_in_archived_category_detail_returns_404(self) -> None:
        response = self.client.get(
            reverse("portal:equipment-detail", args=[self.item_in_archived_category.pk])
        )
        self.assertEqual(response.status_code, 404)

    def test_nonexistent_item_detail_returns_404(self) -> None:
        response = self.client.get(reverse("portal:equipment-detail", args=[999999]))
        self.assertEqual(response.status_code, 404)

    def test_archived_item_photo_returns_404(self) -> None:
        response = self.client.get(reverse("portal:equipment-photo", args=[self.archived_item.pk]))
        self.assertEqual(response.status_code, 404)


class PortalEquipmentInventoryCountsTests(TestCase):
    records: CatalogRecords
    multi_unit_item: CatalogItem

    @classmethod
    def setUpTestData(cls) -> None:
        cls.records = create_catalog_records()
        cls.multi_unit_item = CatalogItem.objects.create(
            category=cls.records.category,
            name="Multi-Unit Rig",
            description="Equipment item with various status units.",
        )
        today = timezone.localdate()
        # 2 AVAILABLE
        EquipmentUnit.objects.create(
            catalog_item=cls.multi_unit_item,
            asset_code="RIG-001",
            condition=UnitCondition.GOOD,
            acquired_on=today,
            status=UnitStatus.AVAILABLE,
        )
        EquipmentUnit.objects.create(
            catalog_item=cls.multi_unit_item,
            asset_code="RIG-002",
            condition=UnitCondition.GOOD,
            acquired_on=today,
            status=UnitStatus.AVAILABLE,
        )
        # 1 RESERVED (serviceable)
        EquipmentUnit.objects.create(
            catalog_item=cls.multi_unit_item,
            asset_code="RIG-003",
            condition=UnitCondition.GOOD,
            acquired_on=today,
            status=UnitStatus.RESERVED,
        )
        # 1 ISSUED (serviceable)
        EquipmentUnit.objects.create(
            catalog_item=cls.multi_unit_item,
            asset_code="RIG-004",
            condition=UnitCondition.GOOD,
            acquired_on=today,
            status=UnitStatus.ISSUED,
        )
        # 1 MAINTENANCE (unserviceable)
        EquipmentUnit.objects.create(
            catalog_item=cls.multi_unit_item,
            asset_code="RIG-005",
            condition=UnitCondition.DAMAGED,
            acquired_on=today,
            status=UnitStatus.MAINTENANCE,
        )
        # 1 RETIRED (unserviceable)
        EquipmentUnit.objects.create(
            catalog_item=cls.multi_unit_item,
            asset_code="RIG-006",
            condition=UnitCondition.FAIR,
            acquired_on=today,
            status=UnitStatus.RETIRED,
        )

    def setUp(self) -> None:
        self.client.force_login(self.records.borrower)

    def test_serviceable_and_available_counts_match_br12_on_list(self) -> None:
        response = self.client.get(
            reverse("portal:equipment-list"), {"q": self.multi_unit_item.name}
        )
        self.assertEqual(response.status_code, 200)
        # 2 available, 4 serviceable (2 available + 1 reserved + 1 issued)
        self.assertContains(response, "2 available")
        self.assertContains(response, "4 serviceable total")

    def test_serviceable_and_available_counts_on_detail(self) -> None:
        response = self.client.get(
            reverse("portal:equipment-detail", args=[self.multi_unit_item.pk])
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'data-testid="portal-item-available"')
        self.assertContains(response, 'data-testid="portal-item-serviceable"')
        self.assertEqual(response.context["item"].available_units, 2)
        self.assertEqual(response.context["item"].serviceable_units, 4)


class PortalEquipmentConfidentialityTests(TestCase):
    records: CatalogRecords
    confidential_item: CatalogItem

    @classmethod
    def setUpTestData(cls) -> None:
        cls.records = create_catalog_records()
        cls.confidential_item = CatalogItem.objects.create(
            category=cls.records.category,
            name="Confidential Lens",
            description="Standard 85mm prime lens.",
        )
        EquipmentUnit.objects.create(
            catalog_item=cls.confidential_item,
            asset_code="SECRET-ASSET-777",
            condition=UnitCondition.GOOD,
            acquired_on=timezone.localdate(),
            status=UnitStatus.AVAILABLE,
            internal_notes="Confidential procurement serial #987654321.",
        )

    def setUp(self) -> None:
        self.client.force_login(self.records.borrower)

    def test_portal_never_exposes_asset_codes_or_internal_notes(self) -> None:
        list_response = self.client.get(
            reverse("portal:equipment-list"), {"q": self.confidential_item.name}
        )
        self.assertEqual(list_response.status_code, 200)
        self.assertNotContains(list_response, "SECRET-ASSET-777")
        self.assertNotContains(list_response, "Confidential procurement serial")

        detail_response = self.client.get(
            reverse("portal:equipment-detail", args=[self.confidential_item.pk])
        )
        self.assertEqual(detail_response.status_code, 200)
        self.assertNotContains(detail_response, "SECRET-ASSET-777")
        self.assertNotContains(detail_response, "Confidential procurement serial")


class PortalEquipmentPhotoTests(TestCase):
    records: CatalogRecords
    photo_item: CatalogItem

    @classmethod
    def setUpTestData(cls) -> None:
        cls.records = create_catalog_records()
        webp_bytes = _generate_test_webp()
        uploaded_file = SimpleUploadedFile("test.webp", webp_bytes, content_type="image/webp")
        cls.photo_item = CatalogItem.objects.create(
            category=cls.records.category,
            name="Photo Drone",
            description="Compact drone with 4K camera.",
            photo=uploaded_file,
        )

    def setUp(self) -> None:
        self.client.force_login(self.records.borrower)

    def test_item_with_photo_streams_webp_with_security_headers(self) -> None:
        url = reverse("portal:equipment-photo", args=[self.photo_item.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "image/webp")
        self.assertEqual(response["X-Content-Type-Options"], "nosniff")
        self.assertEqual(response["Cache-Control"], "private, no-store")

    def test_item_without_photo_photo_route_returns_404(self) -> None:
        url = reverse("portal:equipment-photo", args=[self.records.item.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_template_renders_photo_or_default(self) -> None:
        # Item with photo
        detail_photo = self.client.get(
            reverse("portal:equipment-detail", args=[self.photo_item.pk])
        )
        self.assertContains(
            detail_photo, reverse("portal:equipment-photo", args=[self.photo_item.pk])
        )

        # Item without photo
        detail_default = self.client.get(
            reverse("portal:equipment-detail", args=[self.records.item.pk])
        )
        self.assertContains(detail_default, "default-photo-equipment-270x360.webp")


class PortalEquipmentNavigationTests(TestCase):
    records: CatalogRecords

    @classmethod
    def setUpTestData(cls) -> None:
        cls.records = create_catalog_records()

    def test_equipment_list_and_detail_keep_one_parent_tab_active(self) -> None:
        self.client.force_login(self.records.borrower)
        for url in (
            reverse("portal:equipment-list"),
            reverse("portal:equipment-detail", args=[self.records.item.pk]),
        ):
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, 200)
                nav = NavigationLinks()
                nav.feed(response.content.decode())
                # 5 navigation links in portal (home, equipment, requests, loans, profile in account menu)
                self.assertEqual(len(nav.links), 5)
                # Exactly 1 link active
                self.assertEqual(sum(active for _, active in nav.links), 1)
                # The active link href points to portal:equipment-list
                active_links = [href for href, active in nav.links if active]
                self.assertEqual(active_links, [reverse("portal:equipment-list")])
