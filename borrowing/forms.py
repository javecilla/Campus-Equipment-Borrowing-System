"""Request forms: borrower submission forms/formsets and administrator queue and decision forms."""

from datetime import date

from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator
from django.forms import BaseFormSet, formset_factory
from django.utils import timezone

from borrowing.models import RequestStatus
from inventory.models import CatalogItem
from operations.validation import LoanLimits, validate_requested_due_date

CONTROL_CLASSES: str = "ui-input"
TEXTAREA_CLASSES: str = "ui-input ui-textarea"


class CatalogItemChoiceField(forms.ModelChoiceField):
    """Show borrowers the item and its category instead of a generic model label."""

    def label_from_instance(self, obj: CatalogItem) -> str:
        return f"{obj.name} ({obj.category.name})"


class RequestForm(forms.Form):
    """Validate the borrower-controlled purpose and campus-calendar due date."""

    purpose = forms.CharField(
        label="Purpose",
        strip=True,
        widget=forms.Textarea(attrs={"id": "request-purpose", "class": TEXTAREA_CLASSES}),
    )
    desired_due_date = forms.DateField(
        label="Desired return date",
        input_formats=["%Y-%m-%d"],
        widget=forms.DateInput(
            attrs={"id": "request-due-date", "type": "date", "class": CONTROL_CLASSES},
            format="%Y-%m-%d",
        ),
    )

    def __init__(
        self,
        *args: object,
        limits: LoanLimits,
        submitted_on: date | None = None,
        **kwargs: object,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.limits: LoanLimits = limits
        self.submitted_on: date = submitted_on or timezone.localdate()
        maximum_due_date: date = date.fromordinal(
            min(
                date.max.toordinal(),
                self.submitted_on.toordinal() + self.limits.max_loan_days,
            )
        )
        self.fields["desired_due_date"].widget.attrs.update(
            {
                "min": date.fromordinal(self.submitted_on.toordinal() + 1).isoformat(),
                "max": maximum_due_date.isoformat(),
            }
        )

    def clean_desired_due_date(self) -> date:
        desired_due_date: date = self.cleaned_data["desired_due_date"]
        try:
            return validate_requested_due_date(self.submitted_on, desired_due_date, self.limits)
        except ValidationError as error:
            raise forms.ValidationError(error.messages) from error


class RequestHistoryFilterForm(forms.Form):
    """Validate the optional request-status filter for borrower history."""

    status = forms.ChoiceField(
        label="Status",
        required=False,
        choices=(("", "All statuses"), *RequestStatus.choices),
        widget=forms.Select(
            attrs={
                "id": "request-history-status",
                "class": CONTROL_CLASSES,
            }
        ),
    )


class RequestCancellationForm(forms.Form):
    """Require a CSRF-protected POST confirmation without client-controlled fields."""


class RequestItemForm(forms.Form):
    """Validate one active catalog item and its positive per-item quantity."""

    catalog_item = CatalogItemChoiceField(
        label="Equipment item",
        queryset=CatalogItem.objects.none(),
        empty_label="Choose equipment",
        widget=forms.Select(attrs={"class": CONTROL_CLASSES}),
    )
    quantity = forms.IntegerField(
        label="Quantity",
        min_value=1,
        widget=forms.NumberInput(
            attrs={"class": CONTROL_CLASSES, "min": 1, "inputmode": "numeric"}
        ),
    )

    def __init__(self, *args: object, max_quantity: int, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)
        self.fields["catalog_item"].queryset = (
            CatalogItem.objects.filter(is_archived=False, category__is_archived=False)
            .select_related("category")
            .order_by("name", "pk")
        )
        quantity_field: forms.IntegerField = self.fields["quantity"]
        quantity_field.max_value = max_quantity
        quantity_field.validators.append(MaxValueValidator(max_quantity))
        quantity_field.help_text = f"Maximum per item: {max_quantity}."


class RequestItemFormSet(BaseFormSet):
    """Require one to three complete, distinct item rows on a new request."""

    def clean(self) -> None:
        super().clean()
        if any(self.errors):
            return
        if self.initial_form_count() != 0:
            raise forms.ValidationError("Existing item rows cannot be submitted as a new request.")

        selected_ids: list[int] = [
            form.cleaned_data["catalog_item"].pk for form in self.forms if form.cleaned_data
        ]
        if len(selected_ids) != len(set(selected_ids)):
            raise forms.ValidationError("Choose each catalog item only once.")


RequestItemFormSetFactory = formset_factory(
    RequestItemForm,
    formset=RequestItemFormSet,
    extra=3,
    min_num=1,
    max_num=3,
    validate_min=True,
    validate_max=True,
    absolute_max=3,
)


class RequestQueueForm(forms.Form):
    """Validate optional administrator queue filters before querying requests."""

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
