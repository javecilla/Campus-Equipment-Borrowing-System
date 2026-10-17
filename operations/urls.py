"""Custom management routes supplied as their features are implemented."""

from django.urls import URLPattern, path

from operations import views, workspace_views

app_name = "operations"

urlpatterns: list[URLPattern] = [
    path("", views.dashboard, name="dashboard"),
    path("profile/", views.profile, name="profile"),
    path("settings/", workspace_views.settings, name="settings"),
    path("audit/", workspace_views.audit_list, name="audit-list"),
    path("reports/loans/", workspace_views.loan_report, name="loan-report"),
]
