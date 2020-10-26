from django.http import JsonResponse

from booking.api.material import material_dict


def format_json(request, materialaliases):
    return JsonResponse(
        [
            {
                "id": alias.id,
                "name": alias.name,
                "material": material_dict(request, alias.material),
            }
            for alias in materialaliases
        ],
        safe=False,
    )
