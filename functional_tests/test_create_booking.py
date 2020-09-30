from datetime import timedelta

from django.contrib.auth.models import Permission

from booking.models import PartOfDay
from booking.tests.factories import EventFactory, MaterialFactory
from users.tests.factories import UserFactory, RoleFactory
from .base import FunctionalTest, english
from .game_view_page import GameViewPage


@english
class SimpleUserBookingTest(FunctionalTest):
    def setUp(self):
        super().setUp()

        # Set up roles
        mb_role = RoleFactory(name="MB")
        for perm in [
            # TODO load permissions from common place
            "view_others_groups_bookings",
            "view_category",
            "book_on_privileged_events",
            "view_event",
            "view_location",
            "add_material",
            "change_material",
            "delete_material",
            "view_material",
            "add_materialalias",
            "change_materialalias",
            "delete_materialalias",
            "view_materialalias",
            "add_materialimage",
            "change_materialimage",
            "delete_materialimage",
            "view_materialimage",
            "view_rateclass",
        ]:
            mb_role.permissions.add(Permission.objects.get(codename=perm))

        self.active_event = EventFactory()

        self.materials = MaterialFactory.create_batch(size=10)
        MaterialFactory(name="beschuiten (rol)")
        MaterialFactory(name="EHBO doos")

    def setUpTestData(cls):
        pass

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
