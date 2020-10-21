from django.urls import path

from .views import MaterialDetailView, MaterialDetailModalView
from .views.material_list_view import MaterialListView

app_name = "catalog"
urlpatterns = [
    path("<int:pk>", MaterialDetailView.as_view(), name="material"),
    path("<int:pk>/modal", MaterialDetailModalView.as_view(), name="material_modal"),
    path("", MaterialListView.as_view(), name="catalog"),
]
