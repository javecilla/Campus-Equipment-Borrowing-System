"""Portal routes supplied by the shared authentication task."""

from django.urls import URLPattern, path

from accounts import views

app_name = "portal"

urlpatterns: list[URLPattern] = [
    path("", views.portal_home, name="home"),
]
