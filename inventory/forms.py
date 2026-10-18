from datetime import date
from typing import Any

from django import forms
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import UploadedFile
from django.db.models import Q
from django.http import QueryDict
from django.utils import timezone
from django.utils.datastructures import MultiValueDict

from inventory.models import (
    CatalogItem,
    Category,
    EquipmentUnit,
    UnitCondition,
    UnitStatus,
)
from inventory.photo_forms import EquipmentPhotoForm

CONTROL_CLASSES: str = (
    "h-11 w-full rounded-md border border-slate-200 bg-white px-3 text-sm text-slate-900 "
    "transition-colors hover:border-slate-300 focus:border-accent focus:outline-none "
    "focus:ring-2 focus:ring-accent/15 aria-invalid:border-rose-500"
)

TEXTAREA_CLASSES: str = (
    "w-full rounded-md border border-slate-200 bg-white p-3 text-sm text-slate-900 "
    "transition-colors hover:border-slate-300 focus:border-accent focus:outline-none "
    "focus:ring-2 focus:ring-accent/15 aria-invalid:border-rose-500"
)


class CategoryChoiceField(forms.ModelChoiceField):
    """Identify category choices by their human-readable names."""

    def label_from_instance(self, obj: Category) -> str:
        return obj.name


class CategorySearchForm(forms.Form):
    """Validate optional filters before querying categories."""

    q = forms.CharField(
        label="Search categories",
        required=False,
        max_length=200,
        strip=True,
        widget=forms.SearchInput(
            attrs={
                "id": "category-search-query",
                "class": CONTROL_CLASSES,
                "placeholder": "Search by category name or description...",
            }
        ),
    )
    archived = forms.ChoiceField(
        label="Status",
        required=False,
        choices=(("", "All categories"), ("false", "Active"), ("true", "Archived")),
        widget=forms.Select(attrs={"id": "category-search-archived", "class": CONTROL_CLASSES}),
    )


class CategoryForm(forms.Form):
    """Validate category name and description for creation and updates."""

    name = forms.CharField(
        label="Category name",
        max_length=100,
        required=True,
        strip=True,
        error_messages={"required": "Category name cannot be blank."},
        widget=forms.TextInput(
            attrs={
                "id": "category-name",
                "class": CONTROL_CLASSES,
                "placeholder": "e.g. Cameras, Laptops, Audio Gear",
            }
        ),
    )
    description = forms.CharField(
        label="Description (optional)",
        required=False,
        strip=True,
        widget=forms.Textarea(
            attrs={
                "id": "category-description",
                "rows": 3,
                "class": TEXTAREA_CLASSES,
                "placeholder": "Brief description of the category...",
            }
        ),
    )

    def __init__(self, data: QueryDict | None, category: Category | None) -> None:
        super().__init__(
            data=data,
            initial={"name": category.name, "description": category.description}
            if category is not None
            else None,
        )
        self.instance_id: int | None = category.pk if category is not None else None

    def clean_name(self) -> str:
        name: str = self.cleaned_data.get("name", "").strip()
        if not name:
            raise ValidationError("Category name cannot be blank.")
        existing = Category.objects.filter(name__iexact=name)
        if self.instance_id is not None:
            existing = existing.exclude(pk=self.instance_id)
        if existing.exists():
            raise ValidationError("A category with this name already exists.")
        return name


class CategoryArchiveForm(forms.Form):
    """Confirmation form with CSRF protection for archiving a category."""


class ItemSearchForm(forms.Form):
    """Validate optional filters before querying catalog items."""

    q = forms.CharField(
        label="Search equipment",
        required=False,
        max_length=200,
        strip=True,
        widget=forms.SearchInput(
            attrs={
                "id": "item-search-query",
                "class": CONTROL_CLASSES,
                "placeholder": "Search by item name or description...",
            }
        ),
    )
    category = CategoryChoiceField(
        label="Category",
        required=False,
        queryset=Category.objects.all().order_by("name"),
        empty_label="All categories",
        widget=forms.Select(attrs={"id": "item-search-category", "class": CONTROL_CLASSES}),
    )
    archived = forms.ChoiceField(
        label="Status",
        required=False,
        choices=(("", "All items"), ("false", "Active"), ("true", "Archived")),
        widget=forms.Select(attrs={"id": "item-search-archived", "class": CONTROL_CLASSES}),
    )


class PortalItemSearchForm(forms.Form):
    """Validate optional filters for active equipment catalog items in the borrower portal."""

    q = forms.CharField(
        label="Search equipment",
        required=False,
        max_length=200,
        strip=True,
        widget=forms.SearchInput(
            attrs={
                "id": "portal-item-search-query",
                "class": CONTROL_CLASSES,
                "placeholder": "Search by item name or description...",
            }
        ),
    )
    category = CategoryChoiceField(
        label="Category",
        required=False,
        queryset=Category.objects.none(),
        empty_label="All categories",
        widget=forms.Select(attrs={"id": "portal-item-search-category", "class": CONTROL_CLASSES}),
    )

    def __init__(self, data: QueryDict | None) -> None:
        super().__init__(data=data)
        self.fields["category"].queryset = Category.objects.filter(is_archived=False).order_by(
            "name"
        )


class CatalogItemCreateForm(EquipmentPhotoForm):
    """Validate new catalog item inputs, requiring an active category."""

    category = CategoryChoiceField(
        label="Category",
        required=True,
        queryset=Category.objects.filter(is_archived=False).order_by("name"),
        empty_label="Select a category",
        error_messages={"required": "Category is required."},
        widget=forms.Select(attrs={"id": "item-category", "class": CONTROL_CLASSES}),
    )
    name = forms.CharField(
        label="Item name",
        max_length=150,
        required=True,
        strip=True,
        error_messages={"required": "Item name cannot be blank."},
        widget=forms.TextInput(
            attrs={
                "id": "item-name",
                "class": CONTROL_CLASSES,
                "placeholder": "e.g. Sony Alpha a7 IV, Dell XPS 15",
            }
        ),
    )
    description = forms.CharField(
        label="Borrower-facing description",
        required=True,
        strip=True,
        error_messages={"required": "Item description cannot be blank."},
        widget=forms.Textarea(
            attrs={
                "id": "item-description",
                "rows": 4,
                "class": TEXTAREA_CLASSES,
                "placeholder": "Detailed description of the equipment item, features, and specifications...",
            }
        ),
    )

    def __init__(
        self,
        data: QueryDict | None,
        files: MultiValueDict[str, UploadedFile] | None,
        category_id: str | None,
    ) -> None:
        super().__init__(data=data, files=files, initial={"category": category_id})
        self.fields["photo"].required = False
        self.fields["photo"].label = "Equipment photo (optional)"

    def clean_name(self) -> str:
        name: str = self.cleaned_data.get("name", "").strip()
        if not name:
            raise ValidationError("Item name cannot be blank.")
        return name

    def clean_description(self) -> str:
        description: str = self.cleaned_data.get("description", "").strip()
        if not description:
            raise ValidationError("Item description cannot be blank.")
        return description


class CatalogItemUpdateForm(forms.Form):
    """Validate item edits; category cannot be altered once transactional history exists."""

    category = CategoryChoiceField(
        label="Category",
        required=True,
        queryset=Category.objects.filter(is_archived=False).order_by("name"),
        error_messages={"required": "Category is required."},
        widget=forms.Select(attrs={"id": "item-category", "class": CONTROL_CLASSES}),
    )
    name = forms.CharField(
        label="Item name",
        max_length=150,
        required=True,
        strip=True,
        error_messages={"required": "Item name cannot be blank."},
        widget=forms.TextInput(attrs={"id": "item-name", "class": CONTROL_CLASSES}),
    )
    description = forms.CharField(
        label="Borrower-facing description",
        required=True,
        strip=True,
        error_messages={"required": "Item description cannot be blank."},
        widget=forms.Textarea(
            attrs={"id": "item-description", "rows": 4, "class": TEXTAREA_CLASSES}
        ),
    )

    def __init__(
        self,
        data: QueryDict | None,
        item: CatalogItem,
        has_history: bool,
    ) -> None:
        super().__init__(
            data=data,
            initial={
                "category": item.category_id,
                "name": item.name,
                "description": item.description,
            },
        )
        self.item: CatalogItem = item
        self.has_history: bool = has_history
        self.fields["category"].queryset = Category.objects.filter(
            Q(is_archived=False) | Q(pk=item.category_id)
        ).order_by("name")
        if self.has_history:
            self.fields["category"].disabled = True
            self.fields[
                "category"
            ].help_text = "Category cannot be changed because this item has physical units or borrowing history."
            self.fields["category"].queryset = Category.objects.filter(pk=item.category_id)

    def clean_name(self) -> str:
        name: str = self.cleaned_data.get("name", "").strip()
        if not name:
            raise ValidationError("Item name cannot be blank.")
        return name

    def clean_description(self) -> str:
        description: str = self.cleaned_data.get("description", "").strip()
        if not description:
            raise ValidationError("Item description cannot be blank.")
        return description

    def clean_category(self) -> Category:
        if self.has_history:
            return self.item.category
        category: Category | None = self.cleaned_data.get("category")
        if category is None:
            raise ValidationError("Category is required.")
        if category.is_archived and category.pk != self.item.category_id:
            raise ValidationError("Cannot assign an equipment item to an archived category.")
        return category


class CatalogItemArchiveForm(forms.Form):
    """Confirmation form with CSRF protection for archiving a catalog item."""


class CategoryRestoreForm(forms.Form):
    """Confirmation form accepting no category fields for restoration."""


class CatalogItemRestoreForm(forms.Form):
    """Confirmation form accepting no catalog fields for restoration."""


class CatalogItemChoiceField(forms.ModelChoiceField):
    """Identify equipment choices by their name and category."""

    def label_from_instance(self, obj: CatalogItem) -> str:
        return f"{obj.name} ({obj.category.name})"


class UnitSearchForm(forms.Form):
    """Validate optional filters before querying physical units."""

    q = forms.CharField(
        label="Search units",
        required=False,
        max_length=100,
        strip=True,
        widget=forms.SearchInput(
            attrs={
                "id": "unit-search-query",
                "class": CONTROL_CLASSES,
                "placeholder": "Search by asset code, item, or notes...",
            }
        ),
    )
    category = CategoryChoiceField(
        label="Category",
        required=False,
        queryset=Category.objects.all().order_by("name"),
        empty_label="All categories",
        widget=forms.Select(attrs={"id": "unit-search-category", "class": CONTROL_CLASSES}),
    )
    item = CatalogItemChoiceField(
        label="Equipment item",
        required=False,
        queryset=CatalogItem.objects.select_related("category").order_by("name"),
        empty_label="All items",
        widget=forms.Select(attrs={"id": "unit-search-item", "class": CONTROL_CLASSES}),
    )
    status = forms.ChoiceField(
        label="Status",
        required=False,
        choices=(("", "All statuses"),) + tuple(UnitStatus.choices),
        widget=forms.Select(attrs={"id": "unit-search-status", "class": CONTROL_CLASSES}),
    )


class UnitCreateForm(forms.Form):
    """Validate new physical unit inputs, requiring active item and valid acquisition date."""

    catalog_item = CatalogItemChoiceField(
        label="Equipment item",
        required=True,
        queryset=CatalogItem.objects.filter(is_archived=False, category__is_archived=False)
        .select_related("category")
        .order_by("name"),
        empty_label="Select an equipment item",
        error_messages={"required": "Equipment item is required."},
        widget=forms.Select(attrs={"id": "unit-catalog-item", "class": CONTROL_CLASSES}),
    )
    asset_code = forms.CharField(
        label="Asset code",
        max_length=64,
        required=True,
        strip=True,
        error_messages={"required": "Asset code cannot be blank."},
        widget=forms.TextInput(
            attrs={
                "id": "unit-asset-code",
                "class": CONTROL_CLASSES,
                "placeholder": "e.g. CAM-EOS90D-001",
            }
        ),
    )
    condition = forms.ChoiceField(
        label="Initial condition",
        required=True,
        choices=UnitCondition.choices,
        initial=UnitCondition.GOOD,
        widget=forms.Select(attrs={"id": "unit-condition", "class": CONTROL_CLASSES}),
    )
    acquired_on = forms.DateField(
        label="Acquisition date",
        required=True,
        error_messages={"required": "Acquisition date is required."},
        widget=forms.DateInput(
            attrs={
                "id": "unit-acquired-on",
                "type": "date",
                "class": CONTROL_CLASSES,
            }
        ),
    )
    internal_notes = forms.CharField(
        label="Internal notes (optional)",
        required=False,
        strip=True,
        widget=forms.Textarea(
            attrs={
                "id": "unit-internal-notes",
                "rows": 3,
                "class": TEXTAREA_CLASSES,
                "placeholder": "Administrative notes, serial numbers, supplier details...",
            }
        ),
    )
    maintenance_problem = forms.CharField(
        label="Initial maintenance problem description",
        required=False,
        strip=True,
        widget=forms.Textarea(
            attrs={
                "id": "unit-maintenance-problem",
                "rows": 3,
                "class": TEXTAREA_CLASSES,
                "placeholder": "Required if condition is Damaged. Describe the defect or repair needed...",
            }
        ),
    )

    def __init__(self, data: QueryDict | None, initial_item_id: str | None) -> None:
        initial: dict[str, Any] = {"acquired_on": timezone.localdate()}
        if initial_item_id is not None:
            initial["catalog_item"] = initial_item_id
        super().__init__(data=data, initial=initial)

    def clean_asset_code(self) -> str:
        code: str = self.cleaned_data.get("asset_code", "").strip()
        if not code:
            raise ValidationError("Asset code cannot be blank.")
        if EquipmentUnit.objects.filter(asset_code__iexact=code).exists():
            raise ValidationError("A physical unit with this asset code already exists.")
        return code

    def clean_acquired_on(self) -> date:
        acquired: date | None = self.cleaned_data.get("acquired_on")
        if acquired is None:
            raise ValidationError("Acquisition date is required.")
        if acquired > timezone.localdate():
            raise ValidationError("Acquisition date cannot be in the future.")
        return acquired

    def clean(self) -> dict[str, Any]:
        cleaned_data: dict[str, Any] = super().clean()
        condition: str | None = cleaned_data.get("condition")
        maintenance_problem: str = (cleaned_data.get("maintenance_problem") or "").strip()
        if condition == UnitCondition.DAMAGED and not maintenance_problem:
            self.add_error(
                "maintenance_problem",
                "A maintenance problem description is required when registering a damaged unit.",
            )
        return cleaned_data


class UnitUpdateForm(forms.Form):
    """Validate unit edits; locking fields once transactional history exists."""

    catalog_item = CatalogItemChoiceField(
        label="Equipment item",
        required=True,
        queryset=CatalogItem.objects.all().select_related("category").order_by("name"),
        error_messages={"required": "Equipment item is required."},
        widget=forms.Select(attrs={"id": "unit-catalog-item", "class": CONTROL_CLASSES}),
    )
    asset_code = forms.CharField(
        label="Asset code",
        max_length=64,
        required=True,
        strip=True,
        error_messages={"required": "Asset code cannot be blank."},
        widget=forms.TextInput(attrs={"id": "unit-asset-code", "class": CONTROL_CLASSES}),
    )
    acquired_on = forms.DateField(
        label="Acquisition date",
        required=True,
        error_messages={"required": "Acquisition date is required."},
        widget=forms.DateInput(
            attrs={"id": "unit-acquired-on", "type": "date", "class": CONTROL_CLASSES}
        ),
    )
    internal_notes = forms.CharField(
        label="Internal notes (optional)",
        required=False,
        strip=True,
        widget=forms.Textarea(
            attrs={"id": "unit-internal-notes", "rows": 3, "class": TEXTAREA_CLASSES}
        ),
    )

    def __init__(
        self,
        data: QueryDict | None,
        unit: EquipmentUnit,
        has_history: bool,
    ) -> None:
        super().__init__(
            data=data,
            initial={
                "catalog_item": unit.catalog_item_id,
                "asset_code": unit.asset_code,
                "acquired_on": unit.acquired_on,
                "internal_notes": unit.internal_notes,
            },
        )
        self.unit: EquipmentUnit = unit
        self.has_history: bool = has_history

        self.fields["catalog_item"].queryset = (
            CatalogItem.objects.filter(
                Q(is_archived=False, category__is_archived=False) | Q(pk=unit.catalog_item_id)
            )
            .select_related("category")
            .order_by("name")
        )

        if self.has_history:
            self.fields["catalog_item"].disabled = True
            self.fields[
                "catalog_item"
            ].help_text = "Catalog item cannot be changed because this unit has borrowing or maintenance history."
            self.fields["catalog_item"].queryset = CatalogItem.objects.filter(
                pk=unit.catalog_item_id
            ).select_related("category")
            self.fields["asset_code"].disabled = True
            self.fields[
                "asset_code"
            ].help_text = "Asset code cannot be changed because this unit has borrowing or maintenance history."
            self.fields["acquired_on"].disabled = True
            self.fields[
                "acquired_on"
            ].help_text = "Acquisition date cannot be changed because this unit has borrowing or maintenance history."

    def clean_asset_code(self) -> str:
        if self.has_history:
            return self.unit.asset_code
        code: str = self.cleaned_data.get("asset_code", "").strip()
        if not code:
            raise ValidationError("Asset code cannot be blank.")
        if EquipmentUnit.objects.filter(asset_code__iexact=code).exclude(pk=self.unit.pk).exists():
            raise ValidationError("A physical unit with this asset code already exists.")
        return code

    def clean_acquired_on(self) -> date:
        if self.has_history:
            return self.unit.acquired_on
        acquired: date | None = self.cleaned_data.get("acquired_on")
        if acquired is None:
            raise ValidationError("Acquisition date is required.")
        if acquired > timezone.localdate():
            raise ValidationError("Acquisition date cannot be in the future.")
        return acquired

    def clean_catalog_item(self) -> CatalogItem:
        if self.has_history:
            return self.unit.catalog_item
        item: CatalogItem | None = self.cleaned_data.get("catalog_item")
        if item is None:
            raise ValidationError("Equipment item is required.")
        if (item.is_archived or item.category.is_archived) and item.pk != self.unit.catalog_item_id:
            raise ValidationError(
                "Cannot assign a physical unit to an archived equipment item or category."
            )
        return item
