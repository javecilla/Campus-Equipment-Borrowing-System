"""Allowlisted per-unit return selection; server-side validation covers the whole formset."""

from django import forms
from django.core.exceptions import ValidationError
from django.db.models import QuerySet
from django.forms import BaseFormSet, formset_factory
from django.http import QueryDict

from borrowing.models import LoanUnit
from borrowing.return_services import ReturnInput, validate_returns
from inventory.models import UnitCondition


class ReturnUnitChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj: LoanUnit) -> str:
        return f"{obj.allocation.unit.asset_code} · {obj.allocation.unit.catalog_item.name}"


class ReturnForm(forms.Form):
    selected = forms.BooleanField(label="Return this unit", required=False)
    loan_unit = ReturnUnitChoiceField(
        label="Issued unit",
        queryset=LoanUnit.objects.none(),
        required=False,
        empty_label="Choose an issued unit",
        widget=forms.Select(attrs={"class": "ui-input"}),
    )
    returned_condition = forms.ChoiceField(
        label="Returned condition",
        choices=(("", "Choose condition"), *UnitCondition.choices),
        required=False,
        widget=forms.Select(attrs={"class": "ui-input"}),
    )
    notes = forms.CharField(
        label="Return notes (admin only)",
        required=False,
        widget=forms.Textarea(attrs={"class": "ui-input ui-textarea", "rows": 2}),
    )
    maintenance_problem = forms.CharField(
        label="Maintenance problem (required for Damaged)",
        required=False,
        widget=forms.Textarea(attrs={"class": "ui-input ui-textarea", "rows": 2}),
    )

    def __init__(self, *args: object, loan_units: QuerySet[LoanUnit], **kwargs: object) -> None:
        super().__init__(*args, **kwargs)
        self.fields["loan_unit"].queryset = loan_units
        for name, field in self.fields.items():
            field.widget.attrs["id"] = self.add_prefix(name).replace("_", "-")

    def clean(self) -> dict[str, str | bool | LoanUnit | None]:
        cleaned_data: dict[str, str | bool | LoanUnit | None] = super().clean()
        if cleaned_data.get("selected"):
            if not cleaned_data.get("loan_unit"):
                self.add_error("loan_unit", "Choose an issued unit from this loan.")
            if not cleaned_data.get("returned_condition"):
                self.add_error("returned_condition", "Choose the returned condition.")
            if cleaned_data.get(
                "returned_condition"
            ) == UnitCondition.DAMAGED and not cleaned_data.get("maintenance_problem"):
                self.add_error("maintenance_problem", "Describe the damage requiring maintenance.")
        return cleaned_data


class ReturnFormSet(BaseFormSet):
    def selected_returns(self) -> tuple[ReturnInput, ...]:
        """Call only after is_valid(); unselected rows never produce workflow inputs."""
        return tuple(
            ReturnInput(
                form.cleaned_data["loan_unit"].pk,
                form.cleaned_data["returned_condition"],
                form.cleaned_data["notes"],
                form.cleaned_data["maintenance_problem"],
            )
            for form in self.forms
            if form.cleaned_data.get("selected")
        )

    def clean(self) -> None:
        super().clean()
        if any(self.errors):
            return
        try:
            validate_returns(self.selected_returns())
        except ValidationError as error:
            raise forms.ValidationError(error.messages) from error


def return_formset(data: QueryDict | None, loan_id: int) -> ReturnFormSet:
    """Size forms to outstanding units; choices also allow stale submissions to reach a 409."""
    loan_units: QuerySet[LoanUnit] = (
        LoanUnit.objects.filter(loan_id=loan_id)
        .select_related("allocation__unit__catalog_item")
        .order_by("pk")
    )
    outstanding: list[LoanUnit] = list(loan_units.filter(return_record__isnull=True))
    factory: type[ReturnFormSet] = formset_factory(
        ReturnForm,
        formset=ReturnFormSet,
        extra=0,
        max_num=len(outstanding),
        validate_max=True,
        absolute_max=len(outstanding),
    )
    return factory(
        data=data,
        prefix="returns",
        initial=[{"loan_unit": unit.pk} for unit in outstanding],
        form_kwargs={"loan_units": loan_units},
    )
