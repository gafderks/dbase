from django.urls import path

from . import views

app_name = "booking"
urlpatterns = [
    path("material/new", views.edit_material, name="new_material"),
    path("category/new", views.edit_category, name="new_category"),
    path("category/edit/<int:category_id>", views.edit_category, name="edit_category"),
    path("event/<int:event_id>", views.event_bookings, name="event_bookings"),
    path("api/materials", views.export_materials, name="export_materials"),
]
