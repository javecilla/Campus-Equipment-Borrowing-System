"""Protected navigation destinations; pending modules expose only GET/HEAD pages."""

from django.urls import URLPattern, path

from borrowing import views

app_name = "borrowing_manage"

urlpatterns: list[URLPattern] = [
    path("requests/", views.request_list, name="request-list"),
    path("requests/<int:request_id>/", views.request_detail, name="request-detail"),
    path("requests/<int:request_id>/approve/", views.request_approve, name="request-approve"),
    path("requests/<int:request_id>/reject/", views.request_reject, name="request-reject"),
    path("loans/", views.loan_list, name="loan-list"),
]
