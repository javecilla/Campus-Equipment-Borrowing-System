"""Equipment photo lifecycle against real PostgreSQL and temporary local storage."""

from io import BytesIO
from pathlib import Path
from tempfile import TemporaryDirectory

from django.core.exceptions import PermissionDenied
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import IntegrityError, connection
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from PIL import Image

from inventory.models import CatalogItem
from inventory.photo_services import remove_item_photo, replace_item_photo
from inventory.photos import MAX_PHOTO_BYTES
from operations.models import AuditAction, AuditLog
from operations.tests.records import CatalogRecords, create_catalog_records


def photo_bytes(image_format: str, size: tuple[int, int]) -> bytes:
    output: BytesIO = BytesIO()
    with Image.new("RGB", size, "blue") as image:
        image.save(output, format=image_format)
    return output.getvalue()


def photo_upload(content: bytes) -> SimpleUploadedFile:
    # Neither the client's extension nor its MIME claim determines the saved format.
    return SimpleUploadedFile("../../untrusted-name.png", content, content_type="image/png")


class EquipmentPhotoTests(TestCase):
    records: CatalogRecords
    media_root: Path

    def setUp(self) -> None:
        self.records = create_catalog_records()
        self.media_root = Path(self.enterContext(TemporaryDirectory()))
        self.enterContext(override_settings(MEDIA_ROOT=self.media_root))
        self.client.force_login(self.records.admin)

    def test_upload_replace_download_and_remove(self) -> None:
        item = self.records.item
        detail: str = reverse("inventory_manage:item-detail", args=[item.pk])
        upload: str = reverse("inventory_manage:item-photo-upload", args=[item.pk])
        download: str = reverse("inventory_manage:item-photo", args=[item.pk])
        remove: str = reverse("inventory_manage:item-photo-remove", args=[item.pk])
        self.assertContains(self.client.get(detail), "default-photo-equipment-270x360.webp")
        for image_format in ("PNG", "JPEG", "WEBP"):
            old_name: str = item.photo.name
            with self.captureOnCommitCallbacks(execute=True):
                response = self.client.post(
                    upload, {"photo": photo_upload(photo_bytes(image_format, (2000, 1000)))}
                )
            self.assertRedirects(response, detail)
            item.refresh_from_db()
            self.assertRegex(item.photo.name, r"^equipment/[a-f0-9]{32}\.webp$")
            with Image.open(item.photo.path) as stored:
                self.assertEqual(stored.format, "WEBP")
                self.assertEqual(stored.size, (1600, 800))
            if old_name:
                self.assertFalse((self.media_root / old_name).exists())
            response = self.client.get(download)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response["Content-Type"], "image/webp")
            self.assertEqual(response["Cache-Control"], "private, no-store")
            self.assertEqual(
                b"".join(response.streaming_content), Path(item.photo.path).read_bytes()
            )
        last_path: Path = Path(item.photo.path)
        self.assertEqual(self.client.get(remove).status_code, 200)
        self.assertTrue(last_path.exists())
        with self.captureOnCommitCallbacks(execute=True):
            self.assertRedirects(self.client.post(remove), detail)
        item.refresh_from_db()
        self.assertFalse(item.photo)
        self.assertFalse(last_path.exists())
        self.assertEqual(self.client.post(remove).status_code, 409)
        self.assertEqual(self.client.get(download).status_code, 404)
        self.assertContains(self.client.get(detail), "default-photo-equipment-270x360.webp")
        self.assertEqual(AuditLog.objects.filter(action=AuditAction.ITEM_UPDATED).count(), 4)

    def test_create_item_with_optional_photo_and_reject_invalid_photo_atomically(self) -> None:
        url: str = reverse("inventory_manage:item-create")
        self.assertFalse(self.client.get(url).context["form"].fields["photo"].required)
        before: int = CatalogItem.objects.count()
        for content, expected_status in (
            (b"not an image", 200),
            (photo_bytes("PNG", (40, 30)), 302),
        ):
            response = self.client.post(
                url,
                {
                    "category": self.records.category.pk,
                    "name": "Camera with a creation photo",
                    "description": "Created with its optional equipment photo.",
                    "photo": photo_upload(content),
                },
            )
            self.assertEqual(response.status_code, expected_status)
            if expected_status == 200:
                self.assertIn("photo", response.context["form"].errors)
                self.assertEqual(CatalogItem.objects.count(), before)
                self.assertFalse(tuple(self.media_root.rglob("*.webp")))
                self.assertFalse(AuditLog.objects.filter(action=AuditAction.ITEM_CREATED).exists())
        item: CatalogItem = CatalogItem.objects.get(name="Camera with a creation photo")
        self.assertTrue(Path(item.photo.path).exists())
        self.assertEqual(CatalogItem.objects.count(), before + 1)
        self.assertRedirects(response, reverse("inventory_manage:item-detail", args=[item.pk]))

    def test_create_photo_audit_failure_rolls_back_item_and_file(self) -> None:
        before_items: int = CatalogItem.objects.count()
        before_audit: int = AuditLog.objects.count()
        with connection.cursor() as cursor:
            cursor.execute("SET CONSTRAINTS ALL IMMEDIATE")
            cursor.execute(
                "ALTER TABLE operations_auditlog ADD CONSTRAINT test_reject_create_photo_audit "
                "CHECK (action <> 'ITEM_UPDATED')"
            )
        with self.assertRaises(IntegrityError):
            self.client.post(
                reverse("inventory_manage:item-create"),
                {
                    "category": self.records.category.pk,
                    "name": "Photo creation must roll back",
                    "description": "This item must not survive a photo audit failure.",
                    "photo": photo_upload(photo_bytes("PNG", (30, 30))),
                },
            )
        self.assertEqual(CatalogItem.objects.count(), before_items)
        self.assertEqual(AuditLog.objects.count(), before_audit)
        self.assertFalse(tuple(self.media_root.rglob("*.webp")))

    def test_invalid_photos_do_not_write_files_or_audit(self) -> None:
        upload: str = reverse("inventory_manage:item-photo-upload", args=[self.records.item.pk])
        invalid: tuple[bytes, ...] = (
            b"<script>alert('not an image')</script>",
            b"x" * (MAX_PHOTO_BYTES + 1),
            photo_bytes("GIF", (10, 10)),
            photo_bytes("PNG", (5000, 4100)),
            photo_bytes("JPEG", (30, 30))[:60],
        )
        for content in invalid:
            with self.subTest(size=len(content)):
                response = self.client.post(upload, {"photo": photo_upload(content)})
                self.assertEqual(response.status_code, 200)
                self.assertIn("photo", response.context["form"].errors)
                self.assertFalse(tuple(self.media_root.rglob("*.webp")))
                self.assertFalse(AuditLog.objects.filter(action=AuditAction.ITEM_UPDATED).exists())
        self.records.item.refresh_from_db()
        self.assertFalse(self.records.item.photo)

    def test_orientation_metadata_and_animation_validation(self) -> None:
        upload: str = reverse("inventory_manage:item-photo-upload", args=[self.records.item.pk])
        animated: BytesIO = BytesIO()
        with (
            Image.new("RGB", (20, 10), "blue") as first,
            Image.new("RGB", (20, 10), "red") as second,
        ):
            first.save(animated, format="PNG", save_all=True, append_images=[second])
        response = self.client.post(upload, {"photo": photo_upload(animated.getvalue())})
        self.assertEqual(response.status_code, 200)
        self.assertIn("photo", response.context["form"].errors)
        source: BytesIO = BytesIO()
        with Image.new("RGB", (40, 20), "blue") as image:
            exif: Image.Exif = Image.Exif()
            exif[274] = 6
            exif[270] = "Private image metadata"
            image.save(source, format="JPEG", exif=exif)
        self.assertEqual(
            self.client.post(upload, {"photo": photo_upload(source.getvalue())}).status_code, 302
        )
        self.records.item.refresh_from_db()
        with Image.open(self.records.item.photo.path) as stored:
            self.assertEqual(stored.size, (20, 40))
            self.assertEqual(dict(stored.getexif()), {})

    def test_access_csrf_methods_and_raw_media_are_protected(self) -> None:
        item_id: int = self.records.item.pk
        replace_item_photo(self.records.admin.pk, item_id, photo_bytes("PNG", (30, 30)))
        self.records.item.refresh_from_db()
        for name in ("item-photo", "item-photo-upload", "item-photo-remove"):
            url: str = reverse(f"inventory_manage:{name}", args=[item_id])
            with self.subTest(route=name):
                self.client.logout()
                self.assertEqual(self.client.get(url).status_code, 302)
                self.client.force_login(self.records.borrower)
                self.assertEqual(self.client.get(url).status_code, 403)
                self.assertEqual(
                    self.client.post(url).status_code, 405 if name == "item-photo" else 403
                )
                self.client.force_login(self.records.admin)
                self.assertEqual(self.client.put(url).status_code, 405)
                csrf: Client = Client(enforce_csrf_checks=True)
                csrf.force_login(self.records.admin)
                self.assertEqual(csrf.post(url).status_code, 403)
        self.assertEqual(self.client.get(self.records.item.photo.url).status_code, 404)
        with self.assertRaises(PermissionDenied):
            remove_item_photo(self.records.borrower.pk, item_id)
        self.records.admin.is_active = False
        self.records.admin.save(update_fields=["is_active"])
        with self.assertRaises(PermissionDenied):
            replace_item_photo(self.records.admin.pk, item_id, photo_bytes("PNG", (30, 30)))
        response = self.client.get(reverse("inventory_manage:item-photo", args=[item_id]))
        self.assertEqual(response.status_code, 403)

    def test_audit_failure_preserves_old_photo_and_cleans_new_file(self) -> None:
        item = replace_item_photo(
            self.records.admin.pk, self.records.item.pk, photo_bytes("PNG", (30, 30))
        )
        original_name: str = item.photo.name
        original_bytes: bytes = Path(item.photo.path).read_bytes()
        with connection.cursor() as cursor:
            cursor.execute("SET CONSTRAINTS ALL IMMEDIATE")
            cursor.execute(
                "ALTER TABLE operations_auditlog ADD CONSTRAINT test_reject_photo_audit "
                "CHECK (action <> 'ITEM_UPDATED') NOT VALID"
            )
        with self.assertRaises(IntegrityError):
            replace_item_photo(self.records.admin.pk, item.pk, photo_bytes("PNG", (40, 40)))
        with self.assertRaises(IntegrityError):
            remove_item_photo(self.records.admin.pk, item.pk)
        item.refresh_from_db()
        self.assertEqual(item.photo.name, original_name)
        self.assertEqual(Path(item.photo.path).read_bytes(), original_bytes)
        self.assertEqual(len(tuple(self.media_root.rglob("*.webp"))), 1)
