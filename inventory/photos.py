"""Decode bounded equipment uploads and produce static WebP images without metadata."""

from io import BytesIO

from django.core.exceptions import ValidationError
from PIL import Image, ImageOps, UnidentifiedImageError

MAX_PHOTO_BYTES: int = 5 * 1024 * 1024
MAX_PHOTO_PIXELS: int = 20_000_000


def prepare_equipment_photo(content: bytes) -> bytes:
    """Accept one JPEG/PNG/WebP up to 5 MiB and 20 MP; fit within 1600 pixels."""
    if len(content) > MAX_PHOTO_BYTES:
        raise ValidationError("The equipment photo must be 5 MB or smaller.")
    try:
        with Image.open(BytesIO(content), formats=["JPEG", "PNG", "WEBP"]) as source:
            if source.width * source.height > MAX_PHOTO_PIXELS:
                raise ValidationError(
                    "The equipment photo must contain no more than 20 million pixels."
                )
            if getattr(source, "n_frames", 1) != 1:
                raise ValidationError("Upload a still photo; animated images are not supported.")
            source.load()
            with ImageOps.exif_transpose(source) as oriented, oriented.convert("RGBA") as photo:
                photo.thumbnail((1600, 1600))
                output: BytesIO = BytesIO()
                photo.save(output, format="WEBP", quality=85)
                return output.getvalue()
    except (UnidentifiedImageError, OSError, SyntaxError, Image.DecompressionBombError) as error:
        raise ValidationError("Upload a valid, undamaged JPEG, PNG, or WebP image.") from error
