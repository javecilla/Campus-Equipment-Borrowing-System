"""Protected equipment management routes; pending modules expose only GET/HEAD pages."""

from django.urls import URLPattern, path

from inventory import views

app_name = "inventory_manage"

urlpatterns: list[URLPattern] = [
    path("categories/", views.category_list, name="category-list"),
    path("categories/new/", views.category_create, name="category-create"),
    path("categories/<int:category_id>/", views.category_detail, name="category-detail"),
    path("categories/<int:category_id>/edit/", views.category_update, name="category-update"),
    path("categories/<int:category_id>/archive/", views.category_archive, name="category-archive"),
    path("items/", views.item_list, name="item-list"),
    path("items/new/", views.item_create, name="item-create"),
    path("items/<int:item_id>/", views.item_detail, name="item-detail"),
    path("items/<int:item_id>/edit/", views.item_update, name="item-update"),
    path("items/<int:item_id>/archive/", views.item_archive, name="item-archive"),
    path("units/", views.unit_list, name="unit-list"),
    path("maintenance/", views.maintenance_list, name="maintenance-list"),
]
