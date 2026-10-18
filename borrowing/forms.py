"""Filters for the administrator request queue."""

from django import forms
from django.core.exceptions import ValidationError

from borrowing.models import RequestStatus
from operations.forms import CONTROL_CLASSES


class RequestQueueForm(forms.Form):
    """Validate optional queue filters before querying requests."""

    q = forms.CharField(
        label="Request ID or borrower username",
        required=False,
        max_length=150,
        strip=True,
        widget=forms.SearchInput(
            attrs={
                "id": "request-query",
                "class": CONTROL_CLASSES,
                "placeholder": "Request ID or username",
            }
        ),
    )
    status = forms.ChoiceField(
        label="Status",
        required=False,
        choices=(("", "All statuses"), *RequestStatus.choices),
        widget=forms.Select(attrs={"id": "request-status", "class": CONTROL_CLASSES}),
    )
    date_from = forms.DateField(
        label="Submitted from",
        required=False,
        input_formats=["%Y-%m-%d"],
        widget=forms.DateInput(
            attrs={"id": "request-date-from", "type": "date", "class": CONTROL_CLASSES},
            format="%Y-%m-%d",
        ),
    )
    date_to = forms.DateField(
        label="Submitted through",
        required=False,
        input_formats=["%Y-%m-%d"],
        widget=forms.DateInput(
            attrs={"id": "request-date-to", "type": "date", "class": CONTROL_CLASSES},
            format="%Y-%m-%d",
        ),
    )

    def clean(self):
        cleaned_data = super().clean()
        date_from = cleaned_data.get("date_from")
        date_to = cleaned_data.get("date_to")
        if date_from is not None and date_to is not None and date_from > date_to:
            raise ValidationError("The start date must be on or before the end date.")
        return cleaned_data


class DecisionForm(forms.Form):
    """The written reason that every approval or rejection must carry."""

    reason = forms.CharField(
        label="Reason",
        max_length=500,
        strip=True,
        widget=forms.TextInput(attrs={"id": "decision-reason", "class": CONTROL_CLASSES}),
    )
