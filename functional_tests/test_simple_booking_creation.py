import time
from datetime import timedelta
from unittest import skip

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.utils import timezone
from selenium.webdriver.support.select import Select

from booking.models import Event
from users.models import Group
from .base import FunctionalTest, english
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

from .game_view_page import GameViewPage


def create_user_accounts():
    group_bob_and_charlie = Group(name="Group Bob", slug="group-bob")
    group_alice = Group(name="Group Alice", slug="group-alice")
    group_bob_and_charlie.save()
    group_alice.save()

    User = get_user_model()
    user_bob = User.objects.create_user(
        "bob@example.com", "mypassword", first_name="Bob"
    )
    user_charlie = User.objects.create_user(
        "charlie@example.com", "otherpassword", first_name="Charlie"
    )
    user_alice = User.objects.create_user(
        "alice@example.com", "yetanotherpassword", first_name="Alice"
    )
    user_bob.group = group_bob_and_charlie
    user_charlie.group = group_bob_and_charlie
    user_alice.group = group_alice
    user_bob.save()
    user_charlie.save()
    user_alice.save()


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
        create_user_accounts()

    def test_can_create_booking(self):
        create_events()

        # Bob visits the DBase to book materials for next event
        self.browser.get(self.live_server_url)

        # He notices that he has entered the correct website
        self.assertIn("Material Database", self.browser.title)

        # He gets redirected to the login page
        self.assertIn("/users/login/?next=/", self.browser.current_url)

        # He types his credentials and logs into the DBase
        self.browser.find_element_by_name("username").send_keys("bob@example.com")
        self.browser.find_element_by_name("password").send_keys("mypassword")
        self.browser.find_element_by_name("password").send_keys(Keys.ENTER)

        # He is now logged in
        self.wait_to_be_logged_in("Bob")

        # The active event is 'Active event'
        self.assertEqual(
            self.browser.find_element_by_tag_name("h1").text, "Active event"
        )

        # Hidden event is not displayed
        self.assertNotIn("Hidden event", self.browser.page_source)
        self.assertIn("Active event", self.browser.page_source)

        # Bob may book on the event
        self.assertIn("You may edit", self.browser.page_source)

        # The page shows the group that Bob belongs to his group
        self.assertEqual(
            "Group Bob", self.browser.find_element_by_id("groupSelector").text
        )

        game_view_page = GameViewPage(self)

        # He adds a game to one of the days
        first_game = game_view_page.add_game(
            timezone.now() + timedelta(days=75), "AF", "Hide and seek", "@home"
        )

        # On the game he adds a booking for a material
        beschuit = game_view_page.add_material(first_game, 2, "beschuiten (rol)", "Bes")
