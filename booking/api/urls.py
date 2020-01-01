from django.urls import path

from . import views

app_name = "api"
urlpatterns = [
    path("materials", views.export_materials, name="materials"),
]
