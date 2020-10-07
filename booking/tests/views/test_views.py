from datetime import timedelta

from django.conf import settings
from django.test import TestCase
from django.urls import reverse
from django.utils.timezone import now

from booking.tests.factories import EventFactory
from functional_tests.base import english
from users.tests.factories import UserFactory


class HomeViewTest(TestCase):
    def test_redirects_to_login(self):
        event = EventFactory()
        response = self.client.get("/")
        self.assertRedirects(response, reverse(settings.LOGIN_URL) + "?next=/")

    def test_redirects_to_event(self):
        # There is only one event
        event = EventFactory()
        user = UserFactory()
        self.client.force_login(user)
        response = self.client.get("/")
        self.assertRedirects(response, event.get_absolute_url(), status_code=302)

    @english
    def test_error_if_there_is_no_event(self):
        # There is no event
        user = UserFactory()
        self.client.force_login(user)
        response = self.client.get("/")
        self.assertTemplateUsed(response, "jeugdraad/alert.html")
        self.assertEqual(response.context["message"], "There are no open events.")

    def test_redirects_to_visible_event(self):
        EventFactory.create_batch(4, visible=False)
        visible_event = EventFactory(visible=True)
        user = UserFactory()
        self.client.force_login(user)
        response = self.client.get("/")
        self.assertRedirects(
            response, visible_event.get_absolute_url(), status_code=302
        )

    def test_redirects_to_latest_event(self):
        EventFactory.create_batch(4, event_end=now() + timedelta(days=24))
        latest_event = EventFactory(event_end=now() + timedelta(days=50))
        user = UserFactory()
        self.client.force_login(user)
        response = self.client.get("/")
        self.assertRedirects(response, latest_event.get_absolute_url(), status_code=302)
