import csv
from collections import OrderedDict

from django.http import HttpResponse, JsonResponse
from django.template.defaultfilters import filesizeformat
from django.urls import reverse
from django.utils.translation import gettext as _
from sorl.thumbnail import get_thumbnail


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
        if material.lendable_stock != "":
            stock_header = _("Maximum stock")
            content += (
                f'<p class="max-stock"><span>{stock_header}:</span>'
                f" {material.lendable_stock}</p>"
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
                "sku": mat.sku,
                "tax:product_type": "simple",
                "post_title": mat.name,
                "post_name": mat.name,
                "post_status": "publish" if mat.lendable else "private",
                "tax:product_visibility": "visible"
                if mat.lendable
                else "exclude-from-catalog|exclude-from-search",
                "stock": mat.lendable_stock_value
                if mat.lendable_stock_value is not None
                else mat.stock_value,  # Stock
                "post_content": post_content(mat),
                "regular_price": mat.rate_class.rate.amount
                if mat.rate_class is not None
                else 0.00,
                "tax:product_cat": "|".join(  # join multiple categories
                    [
                        " > ".join(  # add hierarchical categories
                            [
                                str(cat)
                                for cat in category.get_ancestors(include_self=True)
                            ]
                        )
                        for category in mat.categories.all()
                    ]
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


def material_dict(request, material):
    return {
        "id": material.id,
        "name": material.name,
        "categories": [str(category) for category in material.categories.all()],
        "images": [
            request.build_absolute_uri(get_thumbnail(i.image, "32x32").url)
            for i in material.images.all()
        ],
        "gm": material.gm,
        "catalogUrl": reverse("catalog:material_modal", kwargs={"pk": material.id}),
    }


def format_json(request, materials):
    return JsonResponse(
        [material_dict(request, material) for material in materials],
        safe=False,
    )
