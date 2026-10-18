"""Protected equipment management routes; pending modules expose only GET/HEAD pages."""

from django.urls import URLPattern, path

from inventory import photo_views, restore_views, views

app_name = "inventory_manage"

urlpatterns: list[URLPattern] = [
    path("categories/", views.category_list, name="category-list"),
    path("categories/new/", views.category_create, name="category-create"),
    path("categories/<int:category_id>/", views.category_detail, name="category-detail"),
    path("categories/<int:category_id>/edit/", views.category_update, name="category-update"),
    path("categories/<int:category_id>/archive/", views.category_archive, name="category-archive"),
    path(
        "categories/<int:category_id>/restore/",
        restore_views.category_restore,
        name="category-restore",
    ),
    path("items/", views.item_list, name="item-list"),
    path("items/new/", views.item_create, name="item-create"),
    path("items/<int:item_id>/", views.item_detail, name="item-detail"),
    path("items/<int:item_id>/edit/", views.item_update, name="item-update"),
    path("items/<int:item_id>/archive/", views.item_archive, name="item-archive"),
    path("items/<int:item_id>/restore/", restore_views.item_restore, name="item-restore"),
    path("items/<int:item_id>/photo/", photo_views.item_photo, name="item-photo"),
    path(
        "items/<int:item_id>/photo/upload/", photo_views.item_photo_upload, name="item-photo-upload"
    ),
    path(
        "items/<int:item_id>/photo/remove/", photo_views.item_photo_remove, name="item-photo-remove"
    ),
    path("units/", views.unit_list, name="unit-list"),
    path("units/new/", views.unit_create, name="unit-create"),
    path("units/<int:unit_id>/", views.unit_detail, name="unit-detail"),
    path("units/<int:unit_id>/edit/", views.unit_update, name="unit-update"),
    path("maintenance/", views.maintenance_list, name="maintenance-list"),
]
