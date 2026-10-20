"""Borrower-facing equipment catalog browsing, detail, and photo delivery."""

from django.core.paginator import EmptyPage, Page, PageNotAnInteger, Paginator
from django.http import FileResponse, Http404, HttpRequest, HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_safe

from accounts.access import basic_user_required
from inventory.forms import PortalItemSearchForm
from inventory.models import CatalogItem
from inventory.queries import get_active_catalog_item_or_404, list_active_catalog_items


@require_safe
@basic_user_required
def equipment_list(request: HttpRequest) -> HttpResponse:
    """Display active equipment catalog search and category filtering for borrowers."""
    if request.GET:
        form: PortalItemSearchForm = PortalItemSearchForm(request.GET)
        if form.is_valid():
            category = form.cleaned_data["category"]
            items = list_active_catalog_items(
                search_query=form.cleaned_data["q"],
                category_id=category.pk if category else None,
            )
        else:
            items = CatalogItem.objects.none()
    else:
        form = PortalItemSearchForm(None)
        items = list_active_catalog_items(search_query="", category_id=None)

    paginator: Paginator[CatalogItem] = Paginator(items, 10)
    page_number: str = request.GET.get("page", "1")
    try:
        page: Page[CatalogItem] = paginator.page(page_number)
    except (PageNotAnInteger, EmptyPage) as error:
        raise Http404("The requested equipment page does not exist.") from error

    return render(
        request,
        "inventory/portal/equipment_list.html",
        {
            "form": form,
            "page": page,
            "active_portal_tab": "equipment-list",
        },
    )


@require_safe
@basic_user_required
def equipment_detail(request: HttpRequest, item_id: int) -> HttpResponse:
    """Display active equipment item details, serviceable counts, and availability."""
    item: CatalogItem = get_active_catalog_item_or_404(item_id)
    return render(
        request,
        "inventory/portal/equipment_detail.html",
        {
            "item": item,
            "active_portal_tab": "equipment-list",
        },
    )


@require_safe
@basic_user_required
def equipment_photo(request: HttpRequest, item_id: int) -> FileResponse:
    """Stream only the active item's stored photo through the active basic-user boundary."""
    item: CatalogItem = get_active_catalog_item_or_404(item_id)
    if not item.photo:
        raise Http404("This equipment item has no uploaded photo.")
    response: FileResponse = FileResponse(item.photo.open("rb"), content_type="image/webp")
    response["X-Content-Type-Options"] = "nosniff"
    response["Cache-Control"] = "private, no-store"
    return response
