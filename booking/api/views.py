from django.http import HttpResponseBadRequest

from booking.api import material, materialalias
from booking.models import Material, MaterialAlias


def export_material(request):

    materials = Material.objects.prefetch_related("categories", "images").all()
    export_format = request.GET.get("format", "json")

    if export_format == "woocommerce":
        return material.format_woocommerce(request, materials)
    elif export_format == "json":
        return material.format_json(request, materials)
    else:
        return HttpResponseBadRequest("Unknown format")


def export_materialalias(request):

    material_aliases = MaterialAlias.objects.all()

    export_format = request.GET.get("format", "json")

    if export_format == "json":
        return materialalias.format_json(request, material_aliases)
    else:
        return HttpResponseBadRequest("Unknown format")
