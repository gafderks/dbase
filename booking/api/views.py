from django.http import HttpResponseBadRequest

from booking.api import material, materialalias
from booking.models import Material, MaterialAlias


def export_material(request):
    materials = Material.objects.all()

    format = request.GET.get("format", "json")

    if format == "woocommerce":
        return material.format_woocommerce(request, materials)
    elif format == "json":
        return material.format_json(request, materials)
    else:
        return HttpResponseBadRequest("Unknown format")


def export_materialalias(request):
    material_aliases = MaterialAlias.objects.all()

    format = request.GET.get("format", "json")

    if format == "json":
        return materialalias.format_json(request, material_aliases)
    else:
        return HttpResponseBadRequest("Unknown format")
