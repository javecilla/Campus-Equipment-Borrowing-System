"""Portal routes supplied by the shared authentication task."""

from django.urls import URLPattern, path

from accounts import portal_views, views
from borrowing import views as borrowing_views
from inventory import portal_views as inventory_portal_views

app_name = "portal"

urlpatterns: list[URLPattern] = [
    path("", views.portal_home, name="home"),
    path("profile/", portal_views.profile, name="profile"),
    path("equipment/", inventory_portal_views.equipment_list, name="equipment-list"),
    path(
        "equipment/<int:item_id>/",
        inventory_portal_views.equipment_detail,
        name="equipment-detail",
    ),
    path(
        "equipment/<int:item_id>/photo/",
        inventory_portal_views.equipment_photo,
        name="equipment-photo",
    ),
    path("requests/new/", borrowing_views.request_create, name="request-create"),
    path("requests/", portal_views.request_list, name="request-list"),
    path("loans/", portal_views.loan_list, name="loan-list"),
]
