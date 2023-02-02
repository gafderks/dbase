from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DetailView

from booking.mixins import NavigationMixin
from booking.models import Material


class MaterialDetailView(LoginRequiredMixin, NavigationMixin, DetailView):
    template_name = "catalog/material_detail.html"
    model = Material
    queryset = model.objects.select_related("location").prefetch_related(
        "aliases", "attachments", "categories", "images"
    )
