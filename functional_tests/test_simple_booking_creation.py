from datetime import timedelta
from django.core.management import call_command
from django.utils import timezone

from booking.models import Event
from users.models import Group
from .base import FunctionalTest, english

from .game_view_page import GameViewPage


def import_initial_data():
    call_command("importmaterial")
    call_command("creategroups")
    call_command("importfilters")


def create_events():
    def now_plus(days_delta):
        return timezone.now() + timedelta(days=days_delta)

    Event(
        name="Active event",
        slug="active-event",
        booking_start=now_plus(-7),
        booking_end=now_plus(1),
        privileged_booking_end=now_plus(1),
        event_start=now_plus(72),
        event_end=now_plus(82),
    ).save()
    Event(
        name="Privileged event",
        slug="privileged-event",
        booking_start=now_plus(-3),
        booking_end=now_plus(-1),
        privileged_booking_end=now_plus(1),
        event_start=now_plus(3),
        event_end=now_plus(6),
    ).save()
    Event(
        name="Locked event",
        slug="locked-event",
        booking_start=now_plus(-7),
        booking_end=now_plus(1),
        privileged_booking_end=now_plus(1),
        event_start=now_plus(20),
        event_end=now_plus(25),
        locked=True,
    ).save()
    Event(
        name="Locked event 2",
        slug="locked-event-2",
        booking_start=now_plus(-12),
        booking_end=now_plus(-7),
        privileged_booking_end=now_plus(-8),
        event_start=now_plus(55),
        event_end=now_plus(60),
    ).save()
    Event(
        name="Hidden event",
        slug="hidden-event",
        booking_start=now_plus(-7),
        booking_end=now_plus(1),
        privileged_booking_end=now_plus(1),
        event_start=now_plus(20),
        event_end=now_plus(25),
        visible=False,
    ).save()


@english
class SimpleUserBookingTest(FunctionalTest):
    def setUp(self):
        super().setUp()
        import_initial_data()

    def test_can_create_booking(self):
        create_events()

        # Bob is a logged in user
        group_bob = Group.objects.create(name="Group Bob", slug="group-bob")
        self.create_pre_authenticated_session("bob@example.com", group=group_bob)

        # Bob opens the homepage
        self.browser.get(self.live_server_url)

        game_view_page = GameViewPage(self)

        # He adds a game to one of the days
        first_game = game_view_page.add_game(
            timezone.now() + timedelta(days=75), "AF", "Hide and seek", "@home"
        )

        # On the game he adds a booking for a material
        beschuit = game_view_page.add_material(first_game, 2, "beschuiten (rol)", "Bes")
