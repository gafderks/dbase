from django.urls import path

from . import views

app_name = "api"
urlpatterns = [
    path("material", views.export_material, name="material"),
    path("materialalias", views.export_materialalias, name="materialalias"),
]
