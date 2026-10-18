"""Administrator confirmations for restoring archived catalog master records."""

from typing import cast

from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

from accounts.access import admin_required
from accounts.models import User
from inventory.forms import CatalogItemRestoreForm, CategoryRestoreForm
from inventory.models import CatalogItem, Category
from inventory.queries import get_catalog_item_or_404, get_category_or_404
from inventory.services import (
    CategoryRestoreConflict,
    ItemRestoreConflict,
    restore_catalog_item,
    restore_category,
)


@require_http_methods(["GET", "POST"])
@admin_required
def category_restore(request: HttpRequest, category_id: int) -> HttpResponse:
    """Confirm restoration and redirect to the category, or report a stale-state conflict."""
    category: Category = get_category_or_404(category_id)
    form: CategoryRestoreForm = CategoryRestoreForm(
        request.POST if request.method == "POST" else None
    )
    if request.method == "POST" and form.is_valid():
        try:
            restore_category(actor_id=cast(User, request.user).pk, category_id=category.pk)
        except CategoryRestoreConflict as error:
            return render(
                request,
                "inventory/manage/category_restore.html",
                {"category": category, "form": form, "error": str(error)},
                status=409,
            )
        messages.success(request, f'Category "{category.name}" was restored.')
        return redirect("inventory_manage:category-detail", category_id=category.pk)
    return render(
        request,
        "inventory/manage/category_restore.html",
        {"category": category, "form": form},
    )


@require_http_methods(["GET", "POST"])
@admin_required
def item_restore(request: HttpRequest, item_id: int) -> HttpResponse:
    """Restore an item independently while retaining its category's eligibility restriction."""
    item: CatalogItem = get_catalog_item_or_404(item_id)
    form: CatalogItemRestoreForm = CatalogItemRestoreForm(
        request.POST if request.method == "POST" else None
    )
    if request.method == "POST" and form.is_valid():
        try:
            restore_catalog_item(actor_id=cast(User, request.user).pk, item_id=item.pk)
        except ItemRestoreConflict as error:
            return render(
                request,
                "inventory/manage/item_restore.html",
                {"item": item, "form": form, "error": str(error)},
                status=409,
            )
        messages.success(request, f'Equipment item "{item.name}" was restored.')
        return redirect("inventory_manage:item-detail", item_id=item.pk)
    return render(
        request,
        "inventory/manage/item_restore.html",
        {"item": item, "form": form},
    )
