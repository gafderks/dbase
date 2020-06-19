import time
from datetime import date, timedelta
from unittest import skip

from django.contrib.auth import get_user_model
from django.core.management import call_command

from booking.models import Event
from users.models import Group
from .base import FunctionalTest, english
from selenium import webdriver
from selenium.webdriver.common.keys import Keys


def create_user_accounts():
    group_bob_and_charlie = Group(name="Group Bob", slug="group-bob")
    group_alice = Group(name="Group Alice", slug="group-alice")
    group_bob_and_charlie.save()
    group_alice.save()

    User = get_user_model()
    user_bob = User.objects.create_user("bob@example.com", "mypassword")
    user_charlie = User.objects.create_user("charlie@example.com", "otherpassword")
    user_alice = User.objects.create_user("alice@example.com", "yetanotherpassword")
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
        return date.today() + timedelta(days=days_delta)

    Event(
        name="Active event",
        slug="active-event",
        booking_start=now_plus(-7),
        booking_end=now_plus(1),
        privileged_booking_end=now_plus(1),
        event_start=now_plus(20),
        event_end=now_plus(25),
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

        time.sleep(1000)
        # The page

        # Bob may book on the event

        # The page shows the group that Bob belongs to his group

        # He adds a game to the Thursday

        # He notes that the game is added to the page

        # On the game he adds a booking for a material

        # As he types, he gets suggestions for materials

        # Bob decides to add another game

        # Bob changes the order of the games
        self.fail("Finish the test!")

    def test_message_if_no_active_events(self):
        pass

    def test_message_if_user_not_assigned_to_group(self):
        pass

    @skip
    def test_can_start_a_list_for_one_user(self):
        # Edith has heard about a cool new online to-do app. She goes
        # to check out its homepage
        self.browser.get(self.live_server_url)

        # She notices the page title and header mention to-do lists
        self.assertIn("To-Do", self.browser.title)
        header_text = self.browser.find_element_by_tag_name("h1").text
        self.assertIn("To-Do", header_text)

        # She is invited to enter a to-do item straight away
        inputbox = self.get_item_input_box()
        self.assertEqual(inputbox.get_attribute("placeholder"), "Enter a to-do item")

        # She types "Buy peacock feathers" into a text box (Edith's hobby
        # is tying fly-fishing lures)
        inputbox.send_keys("Buy peacock feathers")

        # When she hits enter, the page updates, and now the page lists
        # "1: Buy peacock feathers" as an item in a to-do list table
        inputbox.send_keys(Keys.ENTER)
        self.wait_for_row_in_list_table("1: Buy peacock feathers")

        # There is still a text box inviting her to add another item. She
        # enters "Use peacock feathers to make a fly" (Edith is very
        # methodical)
        self.add_list_item("Use peacock feathers to make a fly")

        # The page updates again, and now shows both items on her list
        self.wait_for_row_in_list_table("2: Use peacock feathers to make a fly")
        self.wait_for_row_in_list_table("1: Buy peacock feathers")

        # Satisfied, she goes back to sleep
