"""Admin-only photo upload, delivery and removal over native Django forms."""

from typing import cast

from django.contrib import messages
from django.core.exceptions import ValidationError
from django.http import FileResponse, Http404, HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods, require_safe

from accounts.access import admin_required
from accounts.models import User
from inventory.models import CatalogItem
from inventory.photo_forms import EquipmentPhotoForm
from inventory.photo_services import ItemPhotoConflict, remove_item_photo, replace_item_photo
from inventory.queries import get_catalog_item_or_404


@require_safe
@admin_required
def item_photo(request: HttpRequest, item_id: int) -> FileResponse:
    """Stream only the item's stored photo through the active administrator boundary."""
    item: CatalogItem = get_catalog_item_or_404(item_id)
    if not item.photo:
        raise Http404("This equipment item has no uploaded photo.")
    response: FileResponse = FileResponse(item.photo.open("rb"), content_type="image/webp")
    response["X-Content-Type-Options"] = "nosniff"
    response["Cache-Control"] = "private, no-store"
    return response


@require_http_methods(["GET", "POST"])
@admin_required
def item_photo_upload(request: HttpRequest, item_id: int) -> HttpResponse:
    item: CatalogItem = get_catalog_item_or_404(item_id)
    form: EquipmentPhotoForm = EquipmentPhotoForm(
        data=request.POST if request.method == "POST" else None,
        files=request.FILES if request.method == "POST" else None,
    )
    if request.method == "POST" and form.is_valid():
        try:
            replace_item_photo(cast(User, request.user).pk, item.pk, form.cleaned_data["photo"])
        except ValidationError as error:
            form.add_error("photo", error)
        else:
            messages.success(request, "Equipment photo saved.")
            return redirect("inventory_manage:item-detail", item_id=item.pk)
    return render(request, "inventory/manage/photo_form.html", {"item": item, "form": form})


@require_http_methods(["GET", "POST"])
@admin_required
def item_photo_remove(request: HttpRequest, item_id: int) -> HttpResponse:
    item: CatalogItem = get_catalog_item_or_404(item_id)
    if request.method == "POST":
        try:
            remove_item_photo(cast(User, request.user).pk, item.pk)
        except ItemPhotoConflict as error:
            return render(
                request,
                "inventory/manage/photo_remove.html",
                {"item": item, "error": str(error)},
                status=409,
            )
        messages.success(request, "Equipment photo removed. The default image is now displayed.")
        return redirect("inventory_manage:item-detail", item_id=item.pk)
    return render(request, "inventory/manage/photo_remove.html", {"item": item})
