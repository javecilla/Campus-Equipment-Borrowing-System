"""Protected navigation destinations; pending modules expose only GET/HEAD pages."""

from django.urls import URLPattern, path

from inventory import views

app_name = "inventory_manage"

urlpatterns: list[URLPattern] = [
    path("items/", views.item_list, name="item-list"),
    path("units/", views.unit_list, name="unit-list"),
    path("maintenance/", views.maintenance_list, name="maintenance-list"),
]
