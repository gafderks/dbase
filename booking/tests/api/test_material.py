import csv
import io
import mimetypes

from bs4 import BeautifulSoup
from django.test import TestCase

from booking.models import Material
from booking.tests.factories import MaterialFactory


class WooCommerceFormatTest(TestCase):
    def check_images(self, field, material):
        """

        :param str field:
        :param Material material:
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
            self.assertIn("testserver", image_url, "url does not contain domain")

    def check_post_content(self, field, material):
        """

        :param str field:
        :param Material material:
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
        attachments = soup.find_all("a", {"target": "attachment"})
        self.assertEqual(len(attachments), material.attachments.count())
        for attachment in attachments:
            attachment_url = attachment["href"]
            response = self.client.get(attachment_url)
            self.assertEqual(response.status_code, 200)
            self.assertIn("testserver", attachment_url, "url does not contain domain")
        # TODO check if stock is part of description

    def test_csv_format(self):
        materials = MaterialFactory.create_batch(10)
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
            self.assertEqual(row["post_status"], "publish")
            if material.lendable:
                self.assertEqual(row["tax:product_visibility"], "visible")
            else:
                self.assertEqual(
                    row["tax:product_visibility"],
                    "exclude-from-catalog|exclude-from-search",
                )
            if material.stock_value is not None:
                self.assertEqual(row["stock"], material.stock_value)
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
                self.assertIn(category.name, row["tax:product_cat"])
            self.check_images(row["images"], material)
            if material.stock_unit is not None:
                self.assertEqual(row["meta:stock_unit"], material.stock_unit)
            else:
                self.assertEqual(row["meta:stock_unit"], "")
