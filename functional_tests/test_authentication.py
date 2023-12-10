from datetime import timedelta

from datetime import timezone
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from booking.models import Event
from tests.utils import english
from users.tests.factories import UserFactory
from .base import FunctionalTest


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
        self.user_bob = UserFactory(password="sekrit")
        create_events()

    def test_can_login_user(self):
        # Bob visits the DBase to book materials for next event
        self.browser.get(self.live_server_url)

        # He notices that he has entered the correct website
        self.assertIn("Material Database", self.browser.title)

        # He gets redirected to the login page
        self.assertIn("/users/login/?next=/", self.browser.current_url)

        # He types his credentials and logs into the DBase
        self.browser.find_element(By.NAME, "username").send_keys(self.user_bob.email)
        self.browser.find_element(By.NAME, "password").send_keys("sekrit")
        self.browser.find_element(By.NAME, "password").send_keys(Keys.ENTER)

        # He is now logged in
        self.wait_to_be_logged_in(self.user_bob.first_name)

        # The active event is 'Active event'
        self.assertEqual(
            self.browser.find_element(By.TAG_NAME, "h1").text, "Active event"
        )

        # Hidden event is not displayed
        self.assertNotIn("Hidden event", self.browser.page_source)
        self.assertIn("Active event", self.browser.page_source)

        # Bob may book on the event
        self.assertIn("You may edit", self.browser.page_source)

        # The page shows the group that Bob belongs to his group
        self.assertEqual(
            self.user_bob.group.name,
            self.browser.find_element(By.ID, "groupSelector").text,
        )
