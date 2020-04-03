from django.urls import path

from camera.views import CameraView, UploadImageView, ListView

app_name = "camera"
urlpatterns = [
    path("", CameraView.as_view(), name="index"),
    path("upload", UploadImageView.as_view(), name="update_image"),
    path("list", ListView.as_view(), name="list"),
]
