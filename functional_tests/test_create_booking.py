from datetime import timedelta

from booking.models import PartOfDay
from booking.tests.factories import EventFactory, MaterialFactory
from users.tests.factories import UserFactory
from .base import FunctionalTest, english
from .game_view_page import GameViewPage


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

    def test_can_edit_booking(self):
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
