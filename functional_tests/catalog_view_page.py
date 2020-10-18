from functional_tests.base import retry_stale, wait


class CatalogViewPage(object):
    def __init__(self, test):
        self.test = test

    @retry_stale  # catalog may contain old material
    @wait  # loading the catalog uses AJAX which may take a while
    def verify_material_attributes(self, catalog_elem, material):
        """
        :param catalog_elem: selenium element
        :param Material material:
        :return:
        """
        # Test if material text is correct
        material_text_elem = catalog_elem.find_element_by_css_selector(".card-title")
        self.test.wait_for(
            lambda: self.test.assertEqual(
                material.name.lower(),
                material_text_elem.text.lower(),
                "the material name does not match",
            )
        )

        # Test if the description is correct
        if material.description:
            description_elem = catalog_elem.find_element_by_class_name(
                "material-description"
            )
            self.test.wait_for(
                lambda: self.test.assertTrue(
                    material.description in description_elem.get_attribute("innerHTML"),
                    "the material description does not match",
                )
            )

        # Test if the stock is correct
        if material.stock_value:
            stock_elem = catalog_elem.find_element_by_class_name("material-stock")
            self.test.wait_for(
                lambda: self.test.assertTrue(
                    material.stock in stock_elem.text,
                    "the material stock does not match",
                )
            )

        # Test if the aliases are correct
        if material.aliases.count() > 0:
            alias_elem = catalog_elem.find_element_by_class_name("material-aliases")
            for alias in material.aliases.all():
                self.test.wait_for(
                    lambda: self.test.assertTrue(
                        str(alias) in alias_elem.text, "an alias does not match"
                    )
                )

        # Test if the attachments are correct
        if material.attachments.count() > 0:
            attachments_elem = catalog_elem.find_element_by_class_name(
                "material-attachments"
            )
            for attachment in material.attachments.all():
                self.test.wait_for(
                    lambda: self.test.assertTrue(
                        attachment.description in attachments_elem.text,
                        "attachment description does not match",
                    )
                )
                self.test.wait_for(
                    lambda: self.test.assertTrue(
                        attachment.attachment.url
                        in attachments_elem.get_attribute("innerHTML"),
                        "attachment URL does not match",
                    )
                )

        # Test if the location is correct
        if material.location:
            location_elem = catalog_elem.find_element_by_class_name("material-location")
            self.test.wait_for(
                lambda: self.test.assertTrue(
                    material.location.name in location_elem.text,
                    "the material location does not match",
                )
            )
