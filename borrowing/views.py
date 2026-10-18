"""Administrator request queue; the loans page remains a placeholder."""

from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_safe

from accounts.access import admin_required
from borrowing.forms import RequestQueueForm
from borrowing.models import BorrowRequest
from borrowing.queries import request_queue


@require_safe
@admin_required
def request_list(request: HttpRequest) -> HttpResponse:
    """Searchable, filterable queue of borrow requests, 25 per page."""
    form = RequestQueueForm(request.GET)
    if form.is_valid():
        queue = request_queue(
            search_query=form.cleaned_data["q"],
            status=form.cleaned_data["status"],
            date_from=form.cleaned_data["date_from"],
            date_to=form.cleaned_data["date_to"],
        )
    else:
        queue = BorrowRequest.objects.none()
    paginator = Paginator(queue, 25)
    try:
        page = paginator.page(request.GET.get("page", "1"))
    except (PageNotAnInteger, EmptyPage) as error:
        raise Http404("The requested queue page does not exist.") from error
    return render(request, "borrowing/manage/request_list.html", {"form": form, "page": page})


@require_safe
@admin_required
def loan_list(request: HttpRequest) -> HttpResponse:
    """Display the pending T15 / T17 · Margareth with Kenneth module without reading or changing domain records."""
    return render(
        request,
        "operations/manage/pending.html",
        {
            "heading": "Releases and returns",
            "module": "T15 / T17 · Margareth with Kenneth",
            "description": "Issued equipment, borrowing slips, due dates, and per-unit returns will appear here.",
            "next_work": "Implement audited one-time release and partial or damaged returns after their prerequisite workflows are integrated.",
        },
    )