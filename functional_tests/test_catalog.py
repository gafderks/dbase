import time

from booking.tests.factories import MaterialFactory, BookingFactory
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
            name="beschuiten (rol)", location__name="in the barn"
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
        # Tests the material details modal from the booking page.
        booking = BookingFactory()

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

    def test_can_view_material_details_modal_list_view(self):
        # Test the material details model from the booking list page.
        booking = BookingFactory()

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
