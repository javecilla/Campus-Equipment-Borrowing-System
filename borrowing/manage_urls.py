"""Protected navigation destinations; pending modules expose only GET/HEAD pages."""

from django.urls import URLPattern, path

from borrowing import views

app_name = "borrowing_manage"

urlpatterns: list[URLPattern] = [
    path("requests/", views.request_list, name="request-list"),
    path("loans/", views.loan_list, name="loan-list"),
]
