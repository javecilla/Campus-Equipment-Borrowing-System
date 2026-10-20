"""Shared file input for optional item creation photos and the separate photo action."""

from django import forms
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import UploadedFile

from inventory.photos import MAX_PHOTO_BYTES


class EquipmentPhotoForm(forms.Form):
    photo = forms.FileField(
        label="Equipment photo",
        help_text="JPEG, PNG or WebP. Maximum 5 MB and 20 million pixels. Use a still image.",
        widget=forms.FileInput(
            attrs={
                "id": "equipment-photo",
                "accept": "image/jpeg,image/png,image/webp",
                "class": "ui-input",
            }
        ),
    )

    def clean_photo(self) -> bytes | None:
        upload: UploadedFile | None = self.cleaned_data["photo"]
        if upload is None:
            return None
        if upload.size > MAX_PHOTO_BYTES:
            raise ValidationError("The equipment photo must be 5 MB or smaller.")
        return upload.read(MAX_PHOTO_BYTES + 1)
