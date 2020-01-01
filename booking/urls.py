from django.urls import path, include

from . import views

app_name = "booking"
urlpatterns = [
    path("category/new", views.edit_category, name="new_category"),
    path("category/edit/<int:category_id>", views.edit_category, name="edit_category"),
    path("event/<int:event_id>", views.event_bookings, name="event_bookings"),
    path("api/", include("booking.api.urls")),
]
