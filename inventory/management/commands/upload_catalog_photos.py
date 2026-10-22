"""Copy referenced local catalog photos into the configured private Neon storage."""

from hashlib import sha256
from pathlib import Path

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.core.management.base import BaseCommand, CommandError

from inventory.models import CatalogItem


def upload_catalog_photos() -> tuple[int, int]:
    """Preserve keys and bytes; reject missing/conflicting files before uploading anything."""
    if settings.STORAGES["default"]["BACKEND"] != "storages.backends.s3.S3Storage":
        raise CommandError("Select MEDIA_STORAGE=neon before running upload_catalog_photos.")
    root: Path = Path(settings.MEDIA_ROOT).resolve()
    names: tuple[str, ...] = tuple(
        CatalogItem.objects.exclude(photo="")
        .order_by("photo")
        .values_list("photo", flat=True)
        .distinct()
    )
    pending: list[tuple[str, bytes]] = []
    retained: int = 0
    for name in names:
        path: Path = (root / name).resolve()
        if not path.is_relative_to(root) or not path.is_file():
            raise CommandError(
                f"Referenced photo {name} is missing from local MEDIA_ROOT or is outside that directory."
            )
        content: bytes = path.read_bytes()
        if default_storage.exists(name):
            with default_storage.open(name, "rb") as remote:
                if sha256(remote.read()).digest() != sha256(content).digest():
                    raise CommandError(
                        f"Remote photo {name} differs from its local source; no existing object was overwritten."
                    )
            retained += 1
        else:
            pending.append((name, content))
    for name, content in pending:
        stored: str = default_storage.save(name, ContentFile(content))
        if stored != name:
            default_storage.delete(stored)
            raise CommandError(
                f"Photo key {name} changed during upload; retry after checking concurrent writers."
            )
        with default_storage.open(name, "rb") as remote:
            if sha256(remote.read()).digest() != sha256(content).digest():
                raise CommandError(
                    f"Uploaded photo {name} failed SHA-256 verification; inspect storage before retrying."
                )
    return len(pending), retained


class Command(BaseCommand):
    help = "Copy all referenced MEDIA_ROOT catalog photos into private Neon storage with unchanged keys and SHA-256 verification. Does not delete originals or update catalog records."

    def handle(self, *args: str, **options: str | int | bool | None) -> None:
        uploaded, retained = upload_catalog_photos()
        self.stdout.write(
            self.style.SUCCESS(
                f"Verified {uploaded} uploaded and {retained} already matching photos. Local originals and catalog references unchanged."
            )
        )
