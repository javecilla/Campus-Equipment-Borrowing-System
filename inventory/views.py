"""Custom category and catalog item views; unit and maintenance workflows remain with their task owners."""

from typing import cast

from django.contrib import messages
from django.core.exceptions import ValidationError
from django.core.paginator import EmptyPage, Page, PageNotAnInteger, Paginator
from django.db.models import QuerySet
from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods, require_safe

from accounts.access import admin_required
from accounts.models import User
from inventory.forms import (
    CatalogItemArchiveForm,
    CatalogItemCreateForm,
    CatalogItemUpdateForm,
    CategoryArchiveForm,
    CategoryForm,
    CategorySearchForm,
    ItemSearchForm,
)
from inventory.models import CatalogItem, Category
from inventory.photo_services import create_catalog_item_with_photo
from inventory.queries import (
    category_items,
    get_catalog_item_or_404,
    get_category_or_404,
    get_item_inventory_counts,
    has_transactional_history,
    list_catalog_items,
    list_categories,
)
from inventory.services import (
    CategoryArchiveConflict,
    ItemArchiveConflict,
    archive_catalog_item,
    archive_category,
    create_catalog_item,
    create_category,
    update_catalog_item,
    update_category,
)


@require_safe
@admin_required
def category_list(request: HttpRequest) -> HttpResponse:
    """List and search equipment categories with strict 25-row pagination."""
    form: CategorySearchForm = CategorySearchForm(request.GET)
    categories: QuerySet[Category]
    if form.is_valid():
        categories = list_categories(
            search_query=form.cleaned_data["q"],
            archived=form.cleaned_data["archived"] or None,
        )
    else:
        categories = Category.objects.none()
    paginator: Paginator[Category] = Paginator(categories, 25)
    try:
        page: Page[Category] = paginator.page(request.GET.get("page", "1"))
    except (PageNotAnInteger, EmptyPage) as error:
        raise Http404("The requested category page does not exist.") from error
    return render(
        request,
        "inventory/manage/category_list.html",
        {"form": form, "page": page},
    )


@require_safe
@admin_required
def category_detail(request: HttpRequest, category_id: int) -> HttpResponse:
    """Display category details and related catalog items with annotated counts."""
    category: Category = get_category_or_404(category_id)
    items: QuerySet[CatalogItem] = category_items(category_id)
    return render(
        request,
        "inventory/manage/category_detail.html",
        {"category": category, "items": items},
    )


@require_http_methods(["GET", "POST"])
@admin_required
def category_create(request: HttpRequest) -> HttpResponse:
    """Validate and persist a new equipment category with transactional audit."""
    form: CategoryForm = CategoryForm(
        request.POST if request.method == "POST" else None,
        category=None,
    )
    if request.method == "POST" and form.is_valid():
        try:
            category: Category = create_category(
                actor_id=cast(User, request.user).pk,
                name=form.cleaned_data["name"],
                description=form.cleaned_data["description"],
            )
        except ValidationError as error:
            form.add_error(None, error)
        else:
            messages.success(request, f'Category "{category.name}" created.')
            return redirect("inventory_manage:category-detail", category_id=category.pk)
    return render(
        request,
        "inventory/manage/category_form.html",
        {"form": form, "title": "New category", "action_label": "Create category"},
    )


@require_http_methods(["GET", "POST"])
@admin_required
def category_update(request: HttpRequest, category_id: int) -> HttpResponse:
    """Validate and update category metadata under row locks."""
    category: Category = get_category_or_404(category_id)
    form: CategoryForm = CategoryForm(
        data=request.POST if request.method == "POST" else None,
        category=category,
    )
    if request.method == "POST" and form.is_valid():
        try:
            category = update_category(
                actor_id=cast(User, request.user).pk,
                category_id=category.pk,
                name=form.cleaned_data["name"],
                description=form.cleaned_data["description"],
            )
        except ValidationError as error:
            form.add_error(None, error)
        else:
            messages.success(request, f'Category "{category.name}" updated.')
            return redirect("inventory_manage:category-detail", category_id=category.pk)
    return render(
        request,
        "inventory/manage/category_form.html",
        {
            "form": form,
            "category": category,
            "title": f"Edit {category.name}",
            "action_label": "Save changes",
        },
    )


@require_http_methods(["GET", "POST"])
@admin_required
def category_archive(request: HttpRequest, category_id: int) -> HttpResponse:
    """Confirm and perform category archival while preserving referenced records."""
    category: Category = get_category_or_404(category_id)
    form: CategoryArchiveForm = CategoryArchiveForm(
        request.POST if request.method == "POST" else None
    )
    if request.method == "POST" and form.is_valid():
        try:
            archive_category(actor_id=cast(User, request.user).pk, category_id=category.pk)
        except CategoryArchiveConflict as error:
            return render(
                request,
                "inventory/manage/category_archive.html",
                {"category": category, "form": form, "error": str(error)},
                status=409,
            )
        messages.success(request, f'Category "{category.name}" was archived.')
        return redirect("inventory_manage:category-detail", category_id=category.pk)
    return render(
        request,
        "inventory/manage/category_archive.html",
        {"category": category, "form": form},
    )


@require_safe
@admin_required
def item_list(request: HttpRequest) -> HttpResponse:
    """List and search catalog items with category filter, derived counts, and pagination."""
    form: ItemSearchForm = ItemSearchForm(request.GET)
    items: QuerySet[CatalogItem]
    if form.is_valid():
        category = form.cleaned_data["category"]
        items = list_catalog_items(
            search_query=form.cleaned_data["q"],
            category_id=category.pk if category else None,
            archived=form.cleaned_data["archived"] or None,
        )
    else:
        items = CatalogItem.objects.none()
    paginator: Paginator[CatalogItem] = Paginator(items, 10)
    try:
        page: Page[CatalogItem] = paginator.page(request.GET.get("page", "1"))
    except (PageNotAnInteger, EmptyPage) as error:
        raise Http404("The requested equipment item page does not exist.") from error
    return render(
        request,
        "inventory/manage/item_list.html",
        {"form": form, "page": page},
    )


@require_safe
@admin_required
def item_detail(request: HttpRequest, item_id: int) -> HttpResponse:
    """Display equipment item details, live derived inventory counts, and physical units."""
    item: CatalogItem = get_catalog_item_or_404(item_id)
    counts = get_item_inventory_counts(item_id)
    has_history: bool = has_transactional_history(item_id)
    units = item.units.all().order_by("asset_code", "pk")
    return render(
        request,
        "inventory/manage/item_detail.html",
        {
            "item": item,
            "counts": counts,
            "has_history": has_history,
            "units": units,
        },
    )


@require_http_methods(["GET", "POST"])
@admin_required
def item_create(request: HttpRequest) -> HttpResponse:
    """Validate and persist a new catalog item under an active category."""
    initial_category_id = request.GET.get("category")
    form: CatalogItemCreateForm = CatalogItemCreateForm(
        data=request.POST if request.method == "POST" else None,
        files=request.FILES if request.method == "POST" else None,
        category_id=initial_category_id,
    )
    if request.method == "POST" and form.is_valid():
        try:
            photo: bytes | None = form.cleaned_data["photo"]
            item: CatalogItem
            if photo is None:
                item = create_catalog_item(
                    actor_id=cast(User, request.user).pk,
                    category_id=form.cleaned_data["category"].pk,
                    name=form.cleaned_data["name"],
                    description=form.cleaned_data["description"],
                )
            else:
                item = create_catalog_item_with_photo(
                    actor_id=cast(User, request.user).pk,
                    category_id=form.cleaned_data["category"].pk,
                    name=form.cleaned_data["name"],
                    description=form.cleaned_data["description"],
                    content=photo,
                )
        except ValidationError as error:
            form.add_error(None, error)
        else:
            messages.success(request, f'Equipment item "{item.name}" created.')
            return redirect("inventory_manage:item-detail", item_id=item.pk)
    return render(
        request,
        "inventory/manage/item_form.html",
        {"form": form, "title": "New equipment item", "action_label": "Create item"},
    )


@require_http_methods(["GET", "POST"])
@admin_required
def item_update(request: HttpRequest, item_id: int) -> HttpResponse:
    """Validate and update catalog item metadata; category change restricted after history."""
    item: CatalogItem = get_catalog_item_or_404(item_id)
    has_history: bool = has_transactional_history(item.pk)
    form: CatalogItemUpdateForm = CatalogItemUpdateForm(
        data=request.POST if request.method == "POST" else None,
        item=item,
        has_history=has_history,
    )
    if request.method == "POST" and form.is_valid():
        new_category = form.cleaned_data["category"]
        category_id: int | None = None if has_history else new_category.pk
        try:
            item = update_catalog_item(
                actor_id=cast(User, request.user).pk,
                item_id=item.pk,
                name=form.cleaned_data["name"],
                description=form.cleaned_data["description"],
                category_id=category_id,
            )
        except ValidationError as error:
            form.add_error(None, error)
        else:
            messages.success(request, f'Equipment item "{item.name}" updated.')
            return redirect("inventory_manage:item-detail", item_id=item.pk)
    return render(
        request,
        "inventory/manage/item_form.html",
        {
            "form": form,
            "item": item,
            "has_history": has_history,
            "title": f"Edit {item.name}",
            "action_label": "Save changes",
        },
    )


@require_http_methods(["GET", "POST"])
@admin_required
def item_archive(request: HttpRequest, item_id: int) -> HttpResponse:
    """Confirm and perform item archival while preserving existing loan workflows."""
    item: CatalogItem = get_catalog_item_or_404(item_id)
    form: CatalogItemArchiveForm = CatalogItemArchiveForm(
        request.POST if request.method == "POST" else None
    )
    if request.method == "POST" and form.is_valid():
        try:
            archive_catalog_item(actor_id=cast(User, request.user).pk, item_id=item.pk)
        except ItemArchiveConflict as error:
            return render(
                request,
                "inventory/manage/item_archive.html",
                {"item": item, "form": form, "error": str(error)},
                status=409,
            )
        messages.success(request, f'Equipment item "{item.name}" was archived.')
        return redirect("inventory_manage:item-detail", item_id=item.pk)
    return render(
        request,
        "inventory/manage/item_archive.html",
        {"item": item, "form": form},
    )


@require_safe
@admin_required
def unit_list(request: HttpRequest) -> HttpResponse:
    """Display the pending T08 · Kenneth module without reading or changing domain records."""
    return render(
        request,
        "operations/manage/pending.html",
        {
            "heading": "Physical units",
            "module": "T08 · Kenneth",
            "description": "Individual campus assets and their availability will appear here.",
            "next_work": "Add asset registration, filters, derived counts, and protected unit history after T07 is integrated.",
        },
    )


@require_safe
@admin_required
def maintenance_list(request: HttpRequest) -> HttpResponse:
    """Display the pending T16 · Kenneth module without reading or changing domain records."""
    return render(
        request,
        "operations/manage/pending.html",
        {
            "heading": "Maintenance",
            "module": "T16 · Kenneth",
            "description": "Equipment repairs, maintenance history, and retirement will be managed here.",
            "next_work": "Add audited maintenance opening and closure after T08. Reserved and issued units must remain protected.",
        },
    )
