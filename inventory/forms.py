"""Allowlisted form inputs and search filters for categories and catalog items."""

from django import forms
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import UploadedFile
from django.db.models import Q
from django.http import QueryDict
from django.utils.datastructures import MultiValueDict

from inventory.models import CatalogItem, Category
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
