from unittest.mock import patch

from django.urls import reverse
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys

from booking.models import Material
from booking.tests.factories import (
    MaterialFactory,
    BookingFactory,
    CategoryFactory,
    EventFactory,
)
from tests.utils import english
from users.tests.factories import UserFactory
from .base import FunctionalTest
from .catalog_view_page import CatalogViewPage
from .game_view_page import GameViewPage
from .list_view_page import ListViewPage


@english
class CatalogMaterialTest(FunctionalTest):
    def setUp(self):
        super().setUp()
        self.material = MaterialFactory(
            name="beschuiten (rol)",
            location__name="in the barn",
            categories=[CategoryFactory()],
        )

    def test_can_view_material_details(self):
        # Tests the material details view

        # Bob is a logged in user
        bob = UserFactory(first_name="Bob")
        self.create_pre_authenticated_session(bob)

        # Bob opens the page for the material
        self.browser.get(self.live_server_url + self.material.get_absolute_url())

        # Bob checks the details for the material
        catalog_view_page = CatalogViewPage(self)
        material_card = self.browser.find_element_by_class_name("material-card")
        catalog_view_page.verify_material_attributes(material_card, self.material)

    def test_can_view_material_details_modal_game_view(self):
        # Tests the material details modal from the booking game page.
        booking = BookingFactory(material__categories=[CategoryFactory()])

        # Bob is a logged in user
        bob = booking.requester
        self.create_pre_authenticated_session(bob)

        # Bob opens the event page
        self.browser.get(self.live_server_url + booking.game.event.get_absolute_url())

        # Bob finds the preloaded booking
        game_view_page = GameViewPage(self)
        booking_id = game_view_page.get_newest_booking_id()
        self.assertEqual(booking_id, booking.pk)

        # Bob clicks on the material name in the booking
        game_view_page.open_catalog_modal(booking_id)

        # Bob sees the details for the booked material
        catalog_view_page = CatalogViewPage(self)
        catalog_view_page.verify_material_attributes(
            game_view_page.get_catalog_modal(), booking.material
        )

        # Bob clicks the category in the modal...
        game_view_page.get_catalog_modal().find_elements_by_css_selector(
            ".category-list a"
        )[0].click()
        # ... to show the material in the catalog
        self.wait_for(
            lambda: self.assertCSSElementExists(
                ".catalog-masonry",
                msg="no masonry with materials was found on the page",
            )
        )

        # Bob clicks the category filter that is active to show all materials
        self.browser.find_element_by_css_selector(
            "button[name=categories].btn-secondary"
        ).click()

        # Bob finds beschuiten (rol) on the page as well
        data_attr = f"/catalog/{self.material.pk}/modal"
        selector = f"[data-catalog-item='{data_attr}']"
        self.wait_for(
            lambda: self.assertCSSElementExists(
                selector,
                "material was not found",
            )
        )

        # Bob inspects the properties of the beschuiten (rol)
        self.browser.find_element_by_css_selector(selector).click()
        catalog_view_page.verify_material_attributes(
            game_view_page.get_catalog_modal(), self.material
        )

    def test_can_view_material_details_modal_list_view(self):
        # Test the material details model from the booking list page.
        booking = BookingFactory(material__categories=[CategoryFactory()])

        # Bob is a logged in user
        bob = booking.requester
        self.create_pre_authenticated_session(bob)

        # Bob opens the event page
        self.browser.get(self.live_server_url + booking.game.event.get_absolute_url())

        # Bob switches to the list view
        game_view_page = GameViewPage(self)
        game_view_page.switch_to_list_view()

        # Bob finds the preloaded booking
        list_view_page = ListViewPage(self)
        booking_id = list_view_page.get_newest_booking_id()
        self.assertEqual(booking_id, booking.pk)

        # Bob clicks on the material name in the booking
        game_view_page.open_catalog_modal(booking_id)

        # Bob sees the details for the booked material
        catalog_view_page = CatalogViewPage(self)
        catalog_view_page.verify_material_attributes(
            list_view_page.get_catalog_modal(), booking.material
        )

        # Bob clicks the category in the modal...
        list_view_page.get_catalog_modal().find_elements_by_css_selector(
            ".category-list a"
        )[0].click()
        # ... to show the material in the catalog
        self.wait_for(
            lambda: self.assertCSSElementExists(
                ".catalog-masonry",
                msg="no masonry with materials was found on the page",
            )
        )

    def test_can_open_catalog_from_event_page(self):
        event = EventFactory()

        # Bob is a logged in user
        bob = UserFactory()
        self.create_pre_authenticated_session(bob)

        # Bob opens the event page
        self.browser.get(self.live_server_url + event.get_absolute_url())

        # Bob finds the button for switching to the catalog
        self.wait_for(
            lambda: self.assertCSSElementExists(".nav-link[href='/catalog/']")
        )

        # Bob switches to the catalog
        self.browser.find_element_by_css_selector(".nav-link[href='/catalog/']").click()

        # Bob sees the catalog masonry
        self.wait_for(
            lambda: self.assertCSSElementExists(
                ".catalog-masonry",
                msg="no masonry with materials was found on the page",
            )
        )

        # Bob finds beschuiten (rol) on the page
        data_attr = f"/catalog/{self.material.pk}/modal"
        selector = f"[data-catalog-item='{data_attr}']"
        self.wait_for(
            lambda: self.assertCSSElementExists(
                selector,
                msg="link to catalog item was not found",
            )
        )

    @patch("catalog.views.MaterialListView.get_paginate_by")
    def test_can_navigate_catalog_page(self, mock_get_paginate_by):
        mock_get_paginate_by.return_value = 2
        category = CategoryFactory()
        # Note there is also the self.material, so 6 materials in total
        materials = MaterialFactory.create_batch(5, categories=[category])
        # Get the materials sorted
        sorted_materials = sorted(
            list(Material.objects.all()), key=lambda m: str(m).lower()
        )

        def verify_material_order(catalog_view_page, i):
            # Get element from page
            item = catalog_view_page.get_catalog_item(i % mock_get_paginate_by())
            # Get text
            text = catalog_view_page.get_catalog_item_text(item)
            self.assertEqual(
                text.lower(),
                str(sorted_materials[i]).lower(),
                f"material {i} is not sorted",
            )

        # Bob is a logged in user
        bob = UserFactory()
        self.create_pre_authenticated_session(bob)

        # Bob opens the catalog page
        self.browser.get(self.live_server_url + reverse("catalog:catalog"))
        catalog_view_page = CatalogViewPage(self)

        # The first page contains the first two materials in order
        verify_material_order(catalog_view_page, 0)
        verify_material_order(catalog_view_page, 1)

        # Bob finds 3 pages in the catalog
        self.assertEqual(catalog_view_page.get_page_count(), 3)

        # Bob can navigate to page 2
        catalog_view_page.navigate_to_page(2)

        # The second page contains the second two materials in order
        verify_material_order(catalog_view_page, 2)
        verify_material_order(catalog_view_page, 3)

        # Bob can navigate to page 3
        catalog_view_page.navigate_to_page(3)

        # The third page contains the third two materials in order
        verify_material_order(catalog_view_page, 4)
        verify_material_order(catalog_view_page, 5)

    def test_navigation_search_material_and_material_alias(self):
        self.browser.set_window_size(1024, 768)
        event = EventFactory()
        material = MaterialFactory()

        # Bob is a logged in user
        bob = UserFactory()
        self.create_pre_authenticated_session(bob)

        # Bob opens the event page
        self.browser.get(self.live_server_url + event.get_absolute_url())

        self.check_if_typeahead_loaded()

        # Bob clicks the search bar and enters the name of the material
        search_input = self.browser.find_element_by_id("navSearch")
        search_input.send_keys(material.name)
        search_input.send_keys(Keys.ENTER)

        # Bob sees the details for the typed material
        catalog_view_page = CatalogViewPage(self)
        catalog_view_page.verify_material_attributes(
            self.browser.find_element_by_id("catalogModal"), material
        )

        # Bob closes the modal by pressing escape
        ActionChains(self.browser).send_keys(Keys.ESCAPE).perform()

        # Bob clicks the search bar and enters the alias of the material
        search_input = self.browser.find_element_by_id("navSearch")
        for _ in range(len(material.name)):
            search_input.send_keys(Keys.BACK_SPACE)
        search_input.send_keys(str(material.aliases.first()))
        search_input.send_keys(Keys.ENTER)  # Choose the suggestion and submit form

        # Bob sees the details for the typed material
        self.wait_for(
            lambda: catalog_view_page.verify_material_attributes(
                self.browser.find_element_by_id("catalogModal"), material
            )
        )
