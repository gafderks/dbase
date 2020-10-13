from django.urls import path

from .views import MaterialDetailView

app_name = "catalog"
urlpatterns = [
    path("<int:pk>", MaterialDetailView.as_view(), name="material"),
]
