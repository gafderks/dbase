from datetime import timedelta

from booking.models import PartOfDay
from booking.tests.factories import EventFactory, MaterialFactory
from booking.tests.factories.game import PopulatedGameFactory
from tests.utils import english
from users.tests.factories import UserFactory
from .base import FunctionalTest
from .game_view_page import GameViewPage
from .list_view_page import ListViewPage


@english
class SimpleUserBookingTest(FunctionalTest):
    def setUp(self):
        super().setUp()
        self.active_event = EventFactory()
        self.materials = MaterialFactory.create_batch(size=10)
        MaterialFactory(name="beschuiten (rol)")
        MaterialFactory(name="EHBO doos")

    def test_can_create_booking(self):
        # Bob is a logged in user
        bob = UserFactory(first_name="Bob")
        self.create_pre_authenticated_session(bob)

        # Bob opens the homepage
        self.browser.get(self.live_server_url)

        game_view_page = GameViewPage(self)

        # He adds a game to one of the days
        first_game = game_view_page.add_game(
            self.active_event.event_start + timedelta(days=4),
            PartOfDay.AFTERNOON,
            "Hide and seek",
            "@home",
        )

        # On the game he adds a booking for a material
        beschuit = game_view_page.add_booking(
            first_game, 2, "beschuiten (rol)", "Beschui"
        )

        # Bob decides to switch to the list view
        game_view_page.switch_to_list_view()
        list_view_page = ListViewPage(self)

        # There, he finds the same booking
        list_view_page.verify_booking_attributes(
            beschuit,
            2,
            "beschuiten (rol)",
            self.active_event.event_start + timedelta(days=4),
            PartOfDay.AFTERNOON,
            "Hide and seek",
        )

    def test_can_edit_booking(self):
        self.browser.set_window_size(1024, 782)

        # Bob is a logged in user
        bob = UserFactory(first_name="Bob")
        self.create_pre_authenticated_session(bob)

        # Bob opens the homepage
        self.browser.get(self.live_server_url)

        game_view_page = GameViewPage(self)

        # He adds a game to one of the days
        first_game_day = self.active_event.event_start + timedelta(days=2)
        first_game = game_view_page.add_game(
            first_game_day,
            PartOfDay.AFTERNOON,
            "Hide and seek",
            "@home",
        )

        # On the game he adds a booking for a material
        beschuit = game_view_page.add_booking(
            first_game, 26, "beschuiten (rol)", "Beschui"
        )

        # Edit the game
        game_view_page.edit_game(
            first_game,
            first_game_day,
            PartOfDay.MORNING,
            "Hike and seek",
            "City center",
        )

        # He adds a booking for another material
        ehbo_doos = game_view_page.add_booking(first_game, 2, "EHBO doos", "doos")

        # Bob edits the booking he just added
        game_view_page.edit_booking(
            ehbo_doos, first_game, 4, "beschuiten (rol)", "Besch"
        )

    def test_can_delete_booking(self):
        self.browser.set_window_size(1024, 782)
        # Bob is a logged in user
        bob = UserFactory(first_name="Bob")

        games = PopulatedGameFactory.create_batch(
            5, creator=bob, event=self.active_event
        )

        self.create_pre_authenticated_session(bob)

        # Bob opens the homepage
        self.browser.get(self.live_server_url)

        game_view_page = GameViewPage(self)

        # Bob deletes one booking from the first game but changes his mind so
        #  he cancels the confirmation
        game_view_page.delete_booking(games[0].bookings.first().pk, cancel=True)

        # Bob deletes a booking from the second game instead
        game_view_page.delete_booking(games[1].bookings.first().pk, cancel=False)

        # Then Bob deletes an entire game (along with its bookings)
        game_view_page.delete_game(games[2].pk, cancel=True)
        game_view_page.delete_game(games[2].pk, cancel=False)
