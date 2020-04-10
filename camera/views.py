import base64
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.core.files.base import ContentFile
from django.db.models import Count
from django.http import JsonResponse
from django.views.generic import TemplateView
from django.views import View

from booking.models import Material, MaterialImage


class CameraView(PermissionRequiredMixin, TemplateView):

    permission_required = "booking.change_material"
    template_name = "camera/camera.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["materials"] = (
            Material.objects.filter()
            .annotate(image_count=Count("images"))
            .order_by(
                "image_count", "lendable", "name"
            )  # Sort materials with images on bottom
        )
        return context


class UploadImageView(PermissionRequiredMixin, View):

    permission_required = "booking.change_material"

    def post(self, request):
        material = Material.objects.get(pk=int(request.POST["material"]))

        _, imgstr = request.POST["image"].split(";base64,")
        image = ContentFile(base64.b64decode(imgstr), name="camera.png")

        material_image = MaterialImage(image=image, material=material).save()
        print(material_image)

        return JsonResponse({"status": "success"})


class ListView(CameraView):

    template_name = "camera/list.html"
