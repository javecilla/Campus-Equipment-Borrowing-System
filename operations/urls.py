"""Custom management routes supplied as their features are implemented."""

from django.urls import URLPattern, path

from operations import views

app_name = "operations"

urlpatterns: list[URLPattern] = [
    path("", views.dashboard, name="dashboard"),
]
