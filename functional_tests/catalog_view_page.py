from functional_tests.base import retry_stale, wait


def filter_number(text):
    # Extracts a number from a text
    return int("".join(filter(str.isdigit, text)))


class CatalogViewPage(object):
    def __init__(self, test):
        self.test = test

    def get_page_count(self):
        self.test.wait_for(
            lambda: self.test.assertTrue(
                len(self.test.browser.find_elements_by_css_selector(".page-link")) > 0
            )
        )
        # -2 skips the previous button
        return int(
            self.test.browser.find_elements_by_css_selector(".page-link")[-2].text
        )

    def navigate_to_page(self, page_num):
        anchor_selector = f"a.page-link[href$='page={page_num}']"
        # wait for the anchor to appear on the page
        self.test.wait_for(
            lambda: self.test.assertTrue(
                len(self.test.browser.find_elements_by_css_selector(anchor_selector))
                > 0
            )
        )
        self.test.browser.find_element_by_css_selector(anchor_selector).click()
        # wait for the page to be loaded
        self.test.wait_for(
            lambda: self.test.assertEqual(
                filter_number(
                    self.test.browser.find_element_by_css_selector(
                        "[aria-current='page']"
                    ).text
                ),
                page_num,
            )
        )

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
