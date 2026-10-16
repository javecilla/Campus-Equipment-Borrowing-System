"""Feature owners add the named custom routes from docs/api_spec.md."""

from django.urls import URLPattern, URLResolver

urlpatterns: list[URLPattern | URLResolver] = []
