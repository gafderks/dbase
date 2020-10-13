from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DetailView

from booking.models import Material


class MaterialDetailView(LoginRequiredMixin, DetailView):

    template_name = "catalog/material_detail.html"
    model = Material
