import csv
import io
import json
import mimetypes

from bs4 import BeautifulSoup
from django.test import TestCase, override_settings

from booking.models import Material
from booking.tests.factories import MaterialFactory, CategoryFactory


@override_settings(SHOP_SKU_OFFSET=2000)
class WooCommerceFormatTest(TestCase):
    def check_images(self, field, material):
        """
        Runs assertions on the images field for a material.
        :param str field: images field
        :param Material material: material that the field is for
        :return: None
        """
        field_images = field.split("|")
        self.assertEqual(
            material.images.count(),
            len(field_images),
            "not all images are included",
        )
        for image_url in field_images:
            mimetype, encoding = mimetypes.guess_type(image_url)
            self.assertTrue(
                mimetype and mimetype.startswith("image"), "url does not seem image"
            )
            self.assertTrue("testserver" in image_url, "url does not contain domain")

    def check_post_content(self, field, material):
        """
        Runs assertions on the post_content for a material.
        :param str field: post_content field
        :param Material material: material that the field is for
        :return: None
        """
        for alias in material.aliases.all():
            self.assertIn(
                alias.name, field, "material alias is not mentioned in post content"
            )
        self.assertTrue(
            bool(BeautifulSoup(field, "html.parser").find()), "invalid HTML"
        )
        self.assertIn(
            material.description, field, "description is not part of post content"
        )
        soup = BeautifulSoup(field, "html.parser")
        attachment_anchors = soup.find_all("a", {"target": "attachment"})
        attachment_urls = [anchor["href"] for anchor in attachment_anchors]
        self.assertEqual(len(attachment_anchors), material.attachments.count())
        for material_attachment in material.attachments.all():
            self.assertIn(
                f"http://testserver{material_attachment.attachment.url}",
                attachment_urls,
            )
        if material.lendable_stock != "":
            self.assertIn(material.lendable_stock, field)

    def test_csv_format(self):
        materials = [
            *MaterialFactory.create_batch(10),
            MaterialFactory.create(
                lendable_stock_value=5, stock_value=4, stock_unit="pieces"
            ),
            MaterialFactory.create(
                lendable_stock_value=None, stock_value=2, stock_unit="pieces"
            ),
        ]
        response = self.client.get("/booking/api/material?format=woocommerce")
        self.assertEqual(
            response.get("Content-Disposition"), 'attachment; filename="materials.csv"'
        )
        self.assertEqual(response.status_code, 200)

        content = response.content.decode("utf-8")

        # Test if all materials are included in CSV + a header
        self.assertEqual(
            len(content.splitlines()),
            len(materials) + 1,
            "not all materials are part of csv",
        )

        csv_reader = csv.DictReader(io.StringIO(content))
        # Verify material attributes
        for row in csv_reader:
            material = Material.objects.get(pk=int(row["sku"]) - 2000)
            self.assertEqual(row["post_title"], material.name)
            self.assertEqual(row["post_name"], material.name)
            if material.lendable:
                self.assertEqual(row["tax:product_visibility"], "visible")
                self.assertEqual(row["post_status"], "publish")
            else:
                self.assertEqual(
                    row["tax:product_visibility"],
                    "exclude-from-catalog|exclude-from-search",
                )
                self.assertEqual(row["post_status"], "private")
            if material.lendable_stock_value is not None:
                self.assertAlmostEqual(
                    float(row["stock"]), material.lendable_stock_value
                )
            elif material.stock_value is not None:
                self.assertAlmostEqual(float(row["stock"]), material.stock_value)
            else:
                self.assertEqual(row["stock"], "")
            self.check_post_content(row["post_content"], material)
            if material.rate_class is not None:
                self.assertEqual(
                    row["regular_price"], str(material.rate_class.rate.amount)
                )
            else:
                self.assertEqual(row["regular_price"], str(0.00))
            for category in material.categories.all():
                self.assertTrue(category.name in row["tax:product_cat"])
            self.check_images(row["images"], material)
            if material.stock_unit is not None:
                self.assertEqual(row["meta:stock_unit"], material.stock_unit)
            else:
                self.assertEqual(row["meta:stock_unit"], "")

    def test_category_tree_hierarchy(self):
        parent = CategoryFactory(name="parent")
        child = CategoryFactory(name="child", parent=parent)
        grandchild = CategoryFactory(name="grandchild", parent=child)
        _ = MaterialFactory(categories=[grandchild])

        response = self.client.get("/booking/api/material?format=woocommerce")
        content = response.content.decode("utf-8")

        csv_reader = csv.DictReader(io.StringIO(content))
        category_csv = next(csv_reader)["tax:product_cat"]
        self.assertEqual(category_csv, "parent > child > grandchild")

    def test_category_tree_multiple(self):
        parent = CategoryFactory(name="parent")
        child = CategoryFactory(name="child", parent=parent)
        _ = MaterialFactory(categories=[child, parent])

        response = self.client.get("/booking/api/material?format=woocommerce")
        content = response.content.decode("utf-8")

        csv_reader = csv.DictReader(io.StringIO(content))
        category_csv = next(csv_reader)["tax:product_cat"]
        self.assertTrue(
            category_csv == "parent > child|parent"
            or category_csv == "parent|parent > child"
        )


class JSONFormatTest(TestCase):
    def test_json_format(self):
        materials = MaterialFactory.create_batch(10)
        response = self.client.get("/booking/api/material?format=json")

        content = str(response.content, encoding="utf8")
        json_response = json.loads(content)

        for item in json_response:
            material = Material.objects.get(pk=int(item["id"]))
            self.assertEqual(item["name"], material.name)
            self.assertEqual(item["gm"], material.gm)
            for category in material.categories.all():
                self.assertTrue(category.name in item["categories"])
            self.assertEqual(
                material.images.count(),
                len(item["images"]),
                "not all images are included",
            )
            for image_url in item["images"]:
                mimetype, encoding = mimetypes.guess_type(image_url)
                self.assertTrue(
                    mimetype and mimetype.startswith("image"), "url does not seem image"
                )
                self.assertTrue(
                    "testserver" in image_url, "url does not contain domain"
                )
            self.assertEqual(item["catalogUrl"], f"/catalog/{material.pk}/modal")
