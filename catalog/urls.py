from django.urls import path

from .views import MaterialDetailView, MaterialDetailModalView, MaterialListView

app_name = "catalog"
urlpatterns = [
    path("<int:pk>", MaterialDetailView.as_view(), name="material"),
    path("<int:pk>/modal", MaterialDetailModalView.as_view(), name="material_modal"),
    path("", MaterialListView.as_view(), name="catalog"),
]
