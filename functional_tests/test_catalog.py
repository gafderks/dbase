from unittest.mock import patch

from django.urls import reverse

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
            lambda: self.assertTrue(
                len(self.browser.find_elements_by_class_name("catalog-masonry")) > 0
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
            lambda: self.assertTrue(
                len(self.browser.find_elements_by_css_selector(selector)) > 0
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
            lambda: self.assertTrue(
                len(self.browser.find_elements_by_class_name("catalog-masonry")) > 0
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
            lambda: self.assertTrue(
                len(
                    self.browser.find_elements_by_css_selector(
                        ".nav-link[href='/catalog/']"
                    )
                )
                > 0
            )
        )

        # Bob switches to the catalog
        self.browser.find_element_by_css_selector(".nav-link[href='/catalog/']").click()

        # Bob sees the catalog masonry
        self.wait_for(
            lambda: self.assertTrue(
                len(self.browser.find_elements_by_class_name("catalog-masonry")) > 0
            )
        )

        # Bob finds beschuiten (rol) on the page
        data_attr = f"/catalog/{self.material.pk}/modal"
        selector = f"[data-catalog-item='{data_attr}']"
        self.wait_for(
            lambda: self.assertTrue(
                len(self.browser.find_elements_by_css_selector(selector)) > 0
            )
        )

    @patch("catalog.views.MaterialListView.get_paginate_by")
    def test_can_navigate_catalog_page(self, mock_get_paginate_by):
        mock_get_paginate_by.return_value = 2
        category = CategoryFactory()
        # Note there is also the self.material, so 6 materials in total
        materials = MaterialFactory.create_batch(5, categories=[category])

        # Bob is a logged in user
        bob = UserFactory()
        self.create_pre_authenticated_session(bob)

        # Bob opens the catalog page
        self.browser.get(self.live_server_url + reverse("catalog:catalog"))

        # Bob finds 3 pages in the catalog
        catalog_view_page = CatalogViewPage(self)
        self.assertEqual(catalog_view_page.get_page_count(), 3)

        # Bob can navigate to page 2
        catalog_view_page.navigate_to_page(2)

        # Bob can navigate to page 3
        catalog_view_page.navigate_to_page(3)

        # TODO check that materials are sorted by name?
