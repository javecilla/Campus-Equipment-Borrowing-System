"""Portal routes supplied by the shared authentication task."""

from django.urls import URLPattern, path

from accounts import portal_views, views
from borrowing import views as borrowing_views

app_name = "portal"

urlpatterns: list[URLPattern] = [
    path("", views.portal_home, name="home"),
    path("profile/", portal_views.profile, name="profile"),
    path("equipment/", portal_views.equipment_list, name="equipment-list"),
    path("requests/new/", borrowing_views.request_create, name="request-create"),
    path("requests/", portal_views.request_list, name="request-list"),
    path("loans/", portal_views.loan_list, name="loan-list"),
]
