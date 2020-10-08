from datetime import timedelta
from unittest.mock import patch

from django.conf import settings
from django.test import TestCase
from django.urls import reverse
from django.utils.timezone import now

from booking.tests.factories import MaterialFactory, EventFactory
from tests.utils import english
from users.tests.factories import UserFactory


class HomeViewTest(TestCase):
    def test_redirects_to_login(self):
        event = EventFactory()
        response = self.client.get("/")
        self.assertRedirects(response, reverse(settings.LOGIN_URL) + "?next=/")

    def test_redirects_to_event(self):
        # There is only one event
        event = EventFactory()
        self.client.force_login(UserFactory())
        response = self.client.get("/")
        self.assertRedirects(response, event.get_absolute_url(), status_code=302)

    @english
    def test_error_if_there_is_no_event(self):
        # There is no event
        self.client.force_login(UserFactory())
        response = self.client.get("/")
        self.assertTemplateUsed(response, "jeugdraad/alert.html")
        self.assertEqual(response.context["message"], "There are no open events.")

    @english
    def test_error_if_there_are_only_hidden_events(self):
        hidden_event = EventFactory(visible=False)
        self.client.force_login(UserFactory())
        response = self.client.get("/")
        self.assertTemplateUsed(response, "jeugdraad/alert.html")
        self.assertEqual(response.context["message"], "There are no open events.")

    @patch("rules.permissions.ObjectPermissionBackend.has_perm")
    def test_only_hidden_events_with_perm(self, mock_has_perm):
        mock_has_perm.return_value = True

        event = EventFactory(visible=False)
        user = UserFactory()
        self.client.force_login(user)
        response = self.client.get("/")
        self.assertRedirects(response, event.get_absolute_url(), status_code=302)
        mock_has_perm.assert_any_call(user, "booking.view_event", event)

    def test_redirects_to_visible_event(self):
        EventFactory.create_batch(4, visible=False)
        visible_event = EventFactory(visible=True)
        self.client.force_login(UserFactory())
        response = self.client.get("/")
        self.assertRedirects(
            response, visible_event.get_absolute_url(), status_code=302
        )

    def test_redirects_to_latest_event(self):
        EventFactory.create_batch(4, event_end=now() + timedelta(days=24))
        latest_event = EventFactory(event_end=now() + timedelta(days=50))
        self.client.force_login(UserFactory())
        response = self.client.get("/")
        self.assertRedirects(response, latest_event.get_absolute_url(), status_code=302)

    def test_typeahead_thumbprint_not_none(self):
        materials = MaterialFactory.create_batch(3)
        last_material = MaterialFactory()
        self.assertNotEqual(materials[0].last_modified, last_material.last_modified)
        self.client.force_login(UserFactory())
        response = self.client.get("/")
        self.assertEqual(
            response.context["typeahead_thumbprint"],
            last_material.last_modified.isoformat(),
            "typeahead thumbprint is not correct",
        )

    def test_typeahead_thumbprint_never(self):
        self.client.force_login(UserFactory())
        response = self.client.get("/")
        self.assertEqual(
            response.context["typeahead_thumbprint"],
            "never",
            "typeahead thumbprint is not correct",
        )
