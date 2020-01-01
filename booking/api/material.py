import csv
from collections import OrderedDict

from django.http import HttpResponse, JsonResponse


def format_woocommerce(request, materials):

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="materials.csv"'

    def line_format(mat):
        """

        :param Material mat:
        :return:
        """
        return OrderedDict(
            {
                "ID": mat.id,
                "Type": "simple",
                "Name": mat.name,
                "Published": 1 if mat.lendable else 0,
                "Visibility in catalog": 1 if mat.lendable else 0,
                "Description": mat.description,
                "Regular price": mat.rate_class.rate
                if mat.rate_class is not None
                else "",
                "Categories": [c.name for c in mat.categories.all()]
                if mat.categories.exists()
                else "",
                "Images": [
                    request.build_absolute_uri(i.image.url) for i in mat.images.all()
                ]
                if mat.images.exists()
                else "",
            }
        )

    writer = csv.DictWriter(response, fieldnames=line_format(materials.first()).keys())
    writer.writeheader()
    for material in materials:
        writer.writerow(line_format(material))

    return response


def format_json(request, materials):
    return JsonResponse(
        [
            {
                "id": material.id,
                "name": material.name,
                "categories": [category.name for category in material.categories.all()],
                "images": [
                    request.build_absolute_uri(i.image.url)
                    for i in material.images.all()
                ],
                "gm": material.gm,
            }
            for material in materials
        ],
        safe=False,
    )
