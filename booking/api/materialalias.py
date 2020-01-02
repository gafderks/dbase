from django.http import JsonResponse


def format_json(request, materialaliases):
    return JsonResponse(
        [
            {
                "id": alias.id,
                "name": alias.name,
                "material": {
                    "id": alias.material.id,
                    "name": alias.material.name,
                    "categories": [
                        category.name for category in alias.material.categories.all()
                    ],
                    "images": [
                        request.build_absolute_uri(i.image.url)
                        for i in alias.material.images.all()
                    ],
                    "gm": alias.material.gm,
                },
            }
            for alias in materialaliases
        ],
        safe=False,
    )
