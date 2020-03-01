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
                "ID": mat.id + 2000,
                "tax:product_type": "simple",
                "post_title": mat.name,
                "post_name": mat.name,
                "post_status": "publish" if mat.lendable else "private",
                "tax:product_visibility": "visible"
                if mat.lendable
                else "exclude-from-catalog|exclude-from-search",
                "stock": mat.stock,  # Stock
                "post_content": mat.description,
                "regular_price": mat.rate_class.rate
                if mat.rate_class is not None
                else "",
                "tax:product_cat": mat.categories.first()
                if mat.categories.exists()
                else "",
                "images": request.build_absolute_uri(mat.images.first().image.url)
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
