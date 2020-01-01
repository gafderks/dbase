from django.http import HttpResponseBadRequest

from booking.api.material import format_woocommerce, format_json
from booking.models import Material


def export_materials(request):
    materials = Material.objects.all()

    format = request.GET.get("format", "json")
    # include_aliases = request.GET.get("include_aliases", False)

    if format == "woocommerce":
        return format_woocommerce(request, materials)
    elif format == "json":
        return format_json(request, materials)
    else:
        return HttpResponseBadRequest("Unknown format")
