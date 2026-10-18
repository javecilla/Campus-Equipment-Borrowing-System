"""Shared account routes."""

from django.urls import URLPattern, path

from accounts import views

app_name = "accounts"

urlpatterns: list[URLPattern] = [
    path("", views.home, name="home"),
    path("accounts/login/", views.login_view, name="login"),
    path("accounts/logout/", views.logout_view, name="logout"),
    path("accounts/register/", views.register_view, name="register"),
    path("manage/accounts/", views.manage_account_list, name="manage-list"),
    path(
        "manage/accounts/<int:account_id>/",
        views.manage_account_detail,
        name="manage-detail",
    ),
    path(
        "manage/accounts/<int:account_id>/activate/",
        views.manage_account_activate,
        name="manage-activate",
    ),
    path(
        "manage/accounts/<int:account_id>/deactivate/",
        views.manage_account_deactivate,
        name="manage-deactivate",
    ),
]
