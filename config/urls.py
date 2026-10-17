"""Root routing for shared authentication and development utilities."""

from django.urls import URLPattern, URLResolver, include, path

from config.views import frontend_test

urlpatterns: list[URLPattern | URLResolver] = [
    path("", include("accounts.urls")),
    path("portal/", include("accounts.portal_urls")),
    path("manage/", include("operations.urls")),
    path("test", frontend_test, name="frontend-test"),
]
