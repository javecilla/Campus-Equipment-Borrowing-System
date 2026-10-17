"""Allowlisted settings inputs and read-only audit search filters."""

from datetime import date
from typing import cast

from django import forms
from django.core.exceptions import ValidationError

from operations.models import AuditAction

CONTROL_CLASSES: str = (
    "h-11 w-full rounded-md border border-slate-200 bg-white px-3 text-sm text-slate-900 "
    "transition-colors hover:border-slate-300 focus:border-accent focus:outline-none "
    "focus:ring-2 focus:ring-accent/15 aria-invalid:border-rose-500"
)


class SettingsForm(forms.Form):
    """Accept the two positive PostgreSQL integer limits, never audit metadata."""

    max_loan_days = forms.IntegerField(
        label="Maximum loan duration (calendar days)",
        min_value=1,
        max_value=2147483647,
        help_text="The due date must be after submission and within this many calendar days.",
        widget=forms.NumberInput(attrs={"id": "max-loan-days", "class": CONTROL_CLASSES}),
    )
    max_quantity_per_item = forms.IntegerField(
        label="Maximum quantity per request item",
        min_value=1,
        max_value=2147483647,
        help_text="The maximum number of units for each catalog item in a new request.",
        widget=forms.NumberInput(attrs={"id": "max-quantity-per-item", "class": CONTROL_CLASSES}),
    )


class AuditSearchForm(forms.Form):
    """Validate optional filters before querying audit history."""

    q = forms.CharField(
        label="Record reference",
        required=False,
        max_length=200,
        strip=True,
        widget=forms.SearchInput(
            attrs={
                "id": "audit-query",
                "class": CONTROL_CLASSES,
                "placeholder": "Model name or record ID",
            }
        ),
    )
    action = forms.ChoiceField(
        label="Action",
        required=False,
        choices=(("", "All actions"), *AuditAction.choices),
        widget=forms.Select(attrs={"id": "audit-action", "class": CONTROL_CLASSES}),
    )
    actor = forms.IntegerField(
        label="Actor account ID",
        required=False,
        min_value=1,
        max_value=9223372036854775807,
        widget=forms.NumberInput(attrs={"id": "audit-actor", "class": CONTROL_CLASSES}),
    )
    date_from = forms.DateField(
        label="Occurred from",
        required=False,
        input_formats=["%Y-%m-%d"],
        widget=forms.DateInput(
            attrs={"id": "audit-date-from", "type": "date", "class": CONTROL_CLASSES},
            format="%Y-%m-%d",
        ),
    )
    date_to = forms.DateField(
        label="Occurred through",
        required=False,
        input_formats=["%Y-%m-%d"],
        widget=forms.DateInput(
            attrs={"id": "audit-date-to", "type": "date", "class": CONTROL_CLASSES},
            format="%Y-%m-%d",
        ),
    )

    def clean(self) -> dict[str, str | int | date | None]:
        cleaned_data: dict[str, str | int | date | None] = super().clean()
        date_from: date | None = cast(date | None, cleaned_data.get("date_from"))
        date_to: date | None = cast(date | None, cleaned_data.get("date_to"))
        if date_from is not None and date_to is not None and date_from > date_to:
            raise ValidationError("The start date must be on or before the end date.")
        return cleaned_data
