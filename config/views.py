"""Development-only pages for verifying shared frontend assets."""

from django.conf import settings
from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_safe


@require_safe
def development_index(request: HttpRequest) -> HttpResponse:
    """Help local developers discover the shared frontend preview."""
    if not settings.DEBUG:
        raise Http404("The development index is available only with DJANGO_DEBUG=True.")
    return render(request, "dev/index.html")


@require_safe
def frontend_test(request: HttpRequest) -> HttpResponse:
    """Display typography and utility samples without reading application data."""
    if not settings.DEBUG:
        raise Http404("The frontend test page is available only with DJANGO_DEBUG=True.")
    return render(request, "dev/frontend-test.html")
