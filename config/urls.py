"""Feature owners add the named custom routes from docs/api_spec.md."""

from django.urls import URLPattern, URLResolver, path

from config.views import development_index, frontend_test

urlpatterns: list[URLPattern | URLResolver] = [
    path("", development_index, name="development-index"),
    path("test", frontend_test, name="frontend-test"),
]
