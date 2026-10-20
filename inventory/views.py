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
    MaintenanceCloseForm,
    MaintenanceCreateForm,
    MaintenanceSearchForm,
    UnitCreateForm,
    UnitSearchForm,
    UnitUpdateForm,
)
from inventory.models import (
    CatalogItem,
    Category,
    EquipmentUnit,
    MaintenanceOutcome,
    MaintenanceRecord,
    MaintenanceStatus,
    UnitCondition,
)
from inventory.photo_services import create_catalog_item_with_photo
from inventory.queries import (
    category_items,
    get_catalog_item_or_404,
    get_category_or_404,
    get_item_inventory_counts,
    get_maintenance_or_404,
    get_overall_inventory_counts,
    get_unit_allocations,
    get_unit_maintenance_records,
    get_unit_or_404,
    has_transactional_history,
    has_unit_transactional_history,
    list_catalog_items,
    list_categories,
    list_equipment_units,
    list_maintenance_records,
)
from inventory.services import (
    CategoryArchiveConflict,
    ItemArchiveConflict,
    MaintenanceConflict,
    archive_catalog_item,
    archive_category,
    close_maintenance,
    create_catalog_item,
    create_category,
    create_equipment_unit,
    open_maintenance,
    update_catalog_item,
    update_category,
    update_equipment_unit,
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
    paginator: Paginator[Category] = Paginator(categories, 5)
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
    """Display paginated physical units matching search, category, item, and status filters."""
    form: UnitSearchForm = UnitSearchForm(request.GET)
    category_id: int | None = None
    if request.GET.get("category"):
        try:
            category_id = int(request.GET["category"])
        except ValueError:
            category_id = None
    item_id: int | None = None
    if request.GET.get("item"):
        try:
            item_id = int(request.GET["item"])
        except ValueError:
            item_id = None
    units: QuerySet[EquipmentUnit] = list_equipment_units(
        search_query=request.GET.get("q", "").strip(),
        category_id=category_id,
        item_id=item_id,
        status=request.GET.get("status") or None,
    )
    counts = get_overall_inventory_counts()
    paginator: Paginator[EquipmentUnit] = Paginator(units, 10)
    try:
        page: Page[EquipmentUnit] = paginator.page(request.GET.get("page", "1"))
    except (PageNotAnInteger, EmptyPage) as error:
        raise Http404("The requested physical unit page does not exist.") from error
    return render(
        request,
        "inventory/manage/unit_list.html",
        {
            "form": form,
            "page": page,
            "counts": counts,
        },
    )


@require_safe
@admin_required
def unit_detail(request: HttpRequest, unit_id: int) -> HttpResponse:
    """Display physical unit details, status, and allocation/loan/maintenance history."""
    unit: EquipmentUnit = get_unit_or_404(unit_id)
    allocations = get_unit_allocations(unit_id)
    maintenance_records = get_unit_maintenance_records(unit_id)
    has_history: bool = has_unit_transactional_history(unit_id)
    return render(
        request,
        "inventory/manage/unit_detail.html",
        {
            "unit": unit,
            "allocations": allocations,
            "maintenance_records": maintenance_records,
            "has_history": has_history,
        },
    )


@require_http_methods(["GET", "POST"])
@admin_required
def unit_create(request: HttpRequest) -> HttpResponse:
    """Validate and register a new physical unit; opens initial maintenance if DAMAGED."""
    initial_item: str | None = request.GET.get("item") or request.GET.get("catalog_item")
    form: UnitCreateForm = UnitCreateForm(
        data=request.POST if request.method == "POST" else None,
        initial_item_id=initial_item,
    )
    if request.method == "POST" and form.is_valid():
        try:
            unit: EquipmentUnit = create_equipment_unit(
                actor_id=cast(User, request.user).pk,
                catalog_item_id=form.cleaned_data["catalog_item"].pk,
                asset_code=form.cleaned_data["asset_code"],
                condition=form.cleaned_data["condition"],
                acquired_on=form.cleaned_data["acquired_on"],
                internal_notes=form.cleaned_data["internal_notes"],
                maintenance_problem=form.cleaned_data.get("maintenance_problem"),
            )
            messages.success(request, f'Physical unit "{unit.asset_code}" registered successfully.')
            return redirect("inventory_manage:unit-detail", unit_id=unit.pk)
        except ValidationError as error:
            form.add_error(None, error)
    return render(
        request,
        "inventory/manage/unit_form.html",
        {
            "form": form,
            "title": "Register physical unit",
            "action_label": "Register physical unit",
            "mode": "create",
        },
    )


@require_http_methods(["GET", "POST"])
@admin_required
def unit_update(request: HttpRequest, unit_id: int) -> HttpResponse:
    """Update physical unit metadata; locking fields once transactional history exists."""
    unit: EquipmentUnit = get_unit_or_404(unit_id)
    has_history: bool = has_unit_transactional_history(unit_id)
    form: UnitUpdateForm = UnitUpdateForm(
        data=request.POST if request.method == "POST" else None,
        unit=unit,
        has_history=has_history,
    )
    if request.method == "POST" and form.is_valid():
        try:
            asset_code: str | None = None
            catalog_item_id: int | None = None
            acquired_on = None
            if not has_history:
                asset_code = form.cleaned_data.get("asset_code")
                if "catalog_item" in form.cleaned_data and form.cleaned_data["catalog_item"]:
                    catalog_item_id = form.cleaned_data["catalog_item"].pk
                acquired_on = form.cleaned_data.get("acquired_on")

            updated_unit: EquipmentUnit = update_equipment_unit(
                actor_id=cast(User, request.user).pk,
                unit_id=unit.pk,
                internal_notes=form.cleaned_data["internal_notes"],
                asset_code=asset_code,
                catalog_item_id=catalog_item_id,
                acquired_on=acquired_on,
            )
            messages.success(request, f'Physical unit "{updated_unit.asset_code}" was updated.')
            return redirect("inventory_manage:unit-detail", unit_id=updated_unit.pk)
        except ValidationError as error:
            form.add_error(None, error)
    return render(
        request,
        "inventory/manage/unit_form.html",
        {
            "form": form,
            "title": f"Edit physical unit {unit.asset_code}",
            "action_label": "Save changes",
            "unit": unit,
            "has_history": has_history,
            "mode": "update",
        },
    )


@require_safe
@admin_required
def maintenance_list(request: HttpRequest) -> HttpResponse:
    """List and search equipment maintenance records with strict 25-row pagination."""
    form: MaintenanceSearchForm = MaintenanceSearchForm(request.GET)
    records: QuerySet[MaintenanceRecord]
    if form.is_valid():
        records = list_maintenance_records(
            search_query=form.cleaned_data["q"],
            status=form.cleaned_data["status"] or None,
        )
    else:
        records = MaintenanceRecord.objects.none()
    paginator: Paginator[MaintenanceRecord] = Paginator(records, 5)
    try:
        page: Page[MaintenanceRecord] = paginator.page(request.GET.get("page", "1"))
    except (PageNotAnInteger, EmptyPage) as error:
        raise Http404("The requested maintenance page does not exist.") from error
    counts = get_overall_inventory_counts()
    return render(
        request,
        "inventory/manage/maintenance_list.html",
        {
            "form": form,
            "page": page,
            "counts": counts,
            "active_tab": "maintenance",
        },
    )


@require_safe
@admin_required
def maintenance_detail(request: HttpRequest, maintenance_id: int) -> HttpResponse:
    """Display maintenance record details, unit status, action taken, and timeline."""
    record: MaintenanceRecord = get_maintenance_or_404(maintenance_id)
    return render(
        request,
        "inventory/manage/maintenance_detail.html",
        {
            "maintenance": record,
            "unit": record.unit,
            "active_tab": "maintenance",
        },
    )


@require_http_methods(["GET", "POST"])
@admin_required
def maintenance_create(request: HttpRequest) -> HttpResponse:
    """Validate and persist manual maintenance opening under row locks and audit."""
    response_status: int = 200
    if request.method == "POST":
        form: MaintenanceCreateForm = MaintenanceCreateForm(data=request.POST, initial_unit_id=None)
        if form.is_valid():
            try:
                selected_unit: EquipmentUnit = form.cleaned_data["unit"]
                maintenance: MaintenanceRecord = open_maintenance(
                    actor_id=cast(User, request.user).pk,
                    unit_id=selected_unit.pk,
                    problem=form.cleaned_data["problem"],
                )
                messages.success(
                    request,
                    f'Maintenance opened for physical unit "{selected_unit.asset_code}".',
                )
                return redirect(
                    "inventory_manage:maintenance-detail", maintenance_id=maintenance.pk
                )
            except MaintenanceConflict as error:
                form.add_error(None, str(error))
                response_status = 409
            except ValidationError as error:
                form.add_error(None, error)
    else:
        form = MaintenanceCreateForm(data=None, initial_unit_id=request.GET.get("unit"))

    return render(
        request,
        "inventory/manage/maintenance_form.html",
        {
            "form": form,
            "title": "Open maintenance",
            "action_label": "Open maintenance",
            "mode": "create",
            "active_tab": "maintenance",
        },
        status=response_status,
    )


@require_http_methods(["GET", "POST"])
@admin_required
def maintenance_close(request: HttpRequest, maintenance_id: int) -> HttpResponse:
    """Close an open maintenance record, reconcile unit status, and audit."""
    record: MaintenanceRecord = get_maintenance_or_404(maintenance_id)
    response_status: int = 200
    form: MaintenanceCloseForm | None = None
    if record.status != MaintenanceStatus.OPEN:
        response_status = 409
    elif request.method == "POST":
        form = MaintenanceCloseForm(data=request.POST)
        if form.is_valid():
            try:
                closed: MaintenanceRecord = close_maintenance(
                    actor_id=cast(User, request.user).pk,
                    maintenance_id=record.pk,
                    action=form.cleaned_data["action"],
                    outcome=form.cleaned_data["outcome"],
                    repaired_condition=form.cleaned_data.get("repaired_condition"),
                )
                outcome_label: str = closed.get_outcome_display()
                messages.success(
                    request,
                    f'Maintenance for "{closed.unit.asset_code}" closed with outcome: {outcome_label}.',
                )
                return redirect("inventory_manage:maintenance-detail", maintenance_id=closed.pk)
            except MaintenanceConflict as error:
                form.add_error(None, str(error))
                response_status = 409
            except ValidationError as error:
                form.add_error(None, error)
    else:
        form = MaintenanceCloseForm(
            initial={
                "outcome": MaintenanceOutcome.AVAILABLE,
                "repaired_condition": (
                    record.unit.condition
                    if record.unit.condition in (UnitCondition.GOOD, UnitCondition.FAIR)
                    else UnitCondition.GOOD
                ),
            }
        )

    return render(
        request,
        "inventory/manage/maintenance_close.html",
        {
            "form": form,
            "error": "This maintenance record is already closed." if form is None else None,
            "maintenance": record,
            "unit": record.unit,
            "title": f"Close maintenance for {record.unit.asset_code}",
            "active_tab": "maintenance",
        },
        status=response_status,
    )
