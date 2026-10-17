"""Shared account routes."""

from django.urls import URLPattern, path

from accounts import views

app_name = "accounts"

urlpatterns: list[URLPattern] = [
    path("", views.home, name="home"),
    path("accounts/login/", views.login_view, name="login"),
    path("accounts/logout/", views.logout_view, name="logout"),
]
