"""Protected navigation destinations for borrowing management."""

from django.urls import URLPattern, path

from borrowing import views

app_name = "borrowing_manage"

urlpatterns: list[URLPattern] = [
    path("requests/", views.request_list, name="request-list"),
    path("requests/<int:request_id>/", views.manage_request_detail, name="request-detail"),
    path("requests/<int:request_id>/approve/", views.request_approve, name="request-approve"),
    path("requests/<int:request_id>/reject/", views.request_reject, name="request-reject"),
    path("requests/<int:request_id>/due-date/", views.request_due_date, name="request-due-date"),
    path("requests/<int:request_id>/release/", views.request_release, name="request-release"),
    path("loans/", views.loan_list, name="loan-list"),
    path("loans/<int:loan_id>/", views.manage_loan_detail, name="loan-detail"),
    path("loans/<int:loan_id>/slip/", views.loan_slip, name="loan-slip"),
]
