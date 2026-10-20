"""Named administrator request decisions, release/return actions and loan pages."""

from django.urls import URLPattern, path

from borrowing import release_views, return_views, views

app_name = "borrowing_manage"

urlpatterns: list[URLPattern] = [
    path("requests/", views.request_list, name="request-list"),
    path("requests/<int:request_id>/", views.manage_request_detail, name="request-detail"),
    path("requests/<int:request_id>/approve/", views.request_approve, name="request-approve"),
    path("requests/<int:request_id>/reject/", views.request_reject, name="request-reject"),
    path(
        "requests/<int:request_id>/due-date/",
        release_views.request_due_date,
        name="request-due-date",
    ),
    path(
        "requests/<int:request_id>/release/", release_views.request_release, name="request-release"
    ),
    path("loans/", release_views.loan_list, name="loan-list"),
    path("loans/<int:loan_id>/", release_views.loan_detail, name="loan-detail"),
    path("loans/<int:loan_id>/slip/", release_views.loan_slip, name="loan-slip"),
    path("loans/<int:loan_id>/returns/new/", return_views.return_create, name="return-create"),
]
