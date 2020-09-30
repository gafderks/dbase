import csv
from collections import OrderedDict

from django.template.defaultfilters import filesizeformat
from sorl.thumbnail import get_thumbnail

from django.http import HttpResponse, JsonResponse
from django.utils.translation import gettext as _


def format_woocommerce(request, materials):

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="materials.csv"'

    def post_content(material):
        content = material.description
        if material.attachments.exists():
            list = [
                f'<li><a href="{request.build_absolute_uri(att.attachment.url)}"'
                f' target="attachment">{att.description} ({att.extension}, '
                f"{filesizeformat(att.attachment.size)})</a></li>"
                for att in material.attachments.all()
            ]
            attachments_header = _("Attachments")
            content += (
                f"<h2>{attachments_header}</h2>"
                f'<ul class="attachments">{"".join(list)}</ul>'
            )
        if material.stock != "":
            stock_header = _("Maximum stock")
            content += (
                f'<p class="max-stock"><span>{stock_header}:</span>'
                f" {material.stock}</p>"
            )
        if material.aliases.exists():
            aliases = [alias.name for alias in material.aliases.all()]
            aliases_header = _("Search terms")
            content += (
                f'<p class="search-terms"><span>{aliases_header}:</span>'
                f" {', '.join(aliases)}</p>"
            )
        return content

    def line_format(mat):
        """
        Format: https://www.webtoffee.com/setting-up-product-import-export-plugin-for-woocommerce/
        :param Material mat:
        :return:
        """
        return OrderedDict(
            {
                "sku": mat.id + 2000,  # avoid collision with simple posts
                "tax:product_type": "simple",
                "post_title": mat.name,
                "post_name": mat.name,
                "post_status": "publish",
                "tax:product_visibility": "visible"
                if mat.lendable
                else "exclude-from-catalog|exclude-from-search",
                "stock": mat.stock_value,  # Stock
                "post_content": post_content(mat),
                "regular_price": mat.rate_class.rate.amount
                if mat.rate_class is not None
                else 0.00,
                "tax:product_cat": "|".join(
                    [str(category) for category in mat.categories.all()]
                ),
                # @see https://www.webtoffee.com/woocommerce-import-products-with-images/
                "images": "|".join(
                    [
                        request.build_absolute_uri(
                            get_thumbnail(img.image, "1280").url
                        )  # At max return HD image (1280x720)
                        for img in mat.images.all()
                    ]
                ),
                "meta:stock_unit": mat.stock_unit,
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
                    request.build_absolute_uri(get_thumbnail(i.image, "32x32").url)
                    for i in material.images.all()
                ],
                "gm": material.gm,
            }
            for material in materials
        ],
        safe=False,
    )
