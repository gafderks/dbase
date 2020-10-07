from datetime import timedelta
from unittest.mock import patch

from django.conf import settings
from django.test import TestCase
from django.urls import reverse
from django.utils.timezone import now

from booking.tests.factories import EventFactory, MaterialFactory
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


class EventViewTest(TestCase):
    ####################################################################################
    # Tests for EventView.get_requested_group
    ####################################################################################

    def test_defaults_to_group_from_user(self):
        event = EventFactory()
        users = UserFactory.create_batch(5)
        self.client.force_login(users[2])
        response = self.client.get(event.get_absolute_url(), follow=True)
        self.assertEqual(
            response.context["current_group"],
            users[2].group,
            "the rendered group is not the user's own group",
        )
        self.assertTemplateUsed(response, "booking/event/event.html")

    @english
    def test_exception_if_user_has_no_group_and_no_perm(self):
        event = EventFactory()
        users = UserFactory.create_batch(5)
        user_without_group = UserFactory(group=None)
        self.client.force_login(user_without_group)
        response = self.client.get(event.get_absolute_url(), follow=True)
        self.assertTemplateUsed(response, "jeugdraad/alert.html")
        self.assertEqual(
            response.context["message"],
            "You are not assigned to a group. Please contact a board member to resolve "
            "this issue.",
        )

    @patch("django.contrib.auth.backends.ModelBackend.has_perm")
    def test_defaults_to_all_if_user_has_no_group_and_perm(self, mock_has_perm):
        mock_has_perm.return_value = True

        event = EventFactory()
        users = UserFactory.create_batch(5)
        user_without_group = UserFactory(group=None)
        self.client.force_login(user_without_group)
        response = self.client.get(event.get_absolute_url(), follow=True)
        self.assertEqual(
            response.context["current_group"], None, "the rendered group is not 'all'"
        )
        self.assertTemplateUsed(response, "booking/event/event.html")
        mock_has_perm.assert_any_call(
            user_without_group, "booking.view_others_groups_bookings", None
        )

    def test_cannot_view_bookings_from_other_group(self):
        event = EventFactory()
        users = UserFactory.create_batch(2)
        self.client.force_login(users[0])
        response = self.client.get(
            reverse(
                "booking:event_games_group",
                kwargs={"event_slug": event.slug, "group_slug": users[1].group.slug},
            ),
            follow=True,
        )
        # The view should default to the users own group
        self.assertEqual(
            response.context["current_group"],
            users[0].group,
            "the rendered group is not the user's own group",
        )
        self.assertTemplateUsed(response, "booking/event/event.html")

    @patch("django.contrib.auth.backends.ModelBackend.has_perm")
    def test_can_view_bookings_from_other_group_with_perm(self, mock_has_perm):
        mock_has_perm.return_value = True

        event = EventFactory()
        users = UserFactory.create_batch(2)
        self.client.force_login(users[0])
        response = self.client.get(
            reverse(
                "booking:event_games_group",
                kwargs={"event_slug": event.slug, "group_slug": users[1].group.slug},
            ),
            follow=True,
        )
        self.assertEqual(
            response.context["current_group"],
            users[1].group,
            "the rendered group is not the requested group",
        )
        self.assertTemplateUsed(response, "booking/event/event.html")
        mock_has_perm.assert_any_call(
            users[0], "booking.view_others_groups_bookings", None
        )

    ####################################################################################
    # Tests for EventView.get_requested_event
    ####################################################################################

    def test_view_event(self):
        event = EventFactory()
        self.client.force_login(UserFactory())
        response = self.client.get(event.get_absolute_url())
        self.assertEqual(
            response.context["current_event"],
            event,
            "the rendered event is not the requested event",
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed("booking/event/event.html")

    def test_cannot_view_nonexisting_event(self):
        self.client.force_login(UserFactory())
        response = self.client.get(
            reverse("booking:event_games", kwargs={"event_slug": "fake-event"})
        )
        self.assertEqual(
            response.status_code,
            404,
            "non-existing event should return a 404 status code",
        )

    @english
    def test_cannot_view_hidden_event(self):
        event = EventFactory(visible=False)
        self.client.force_login(UserFactory())
        response = self.client.get(event.get_absolute_url())
        self.assertTemplateUsed(response, "jeugdraad/alert.html")
        self.assertEqual(
            response.context["message"], "You are not allowed to view this event"
        )

    @patch("rules.permissions.ObjectPermissionBackend.has_perm")
    def test_view_hidden_event_with_perm(self, mock_has_perm):
        mock_has_perm.return_value = True

        event = EventFactory(visible=False)
        user = UserFactory()
        self.client.force_login(user)
        response = self.client.get(event.get_absolute_url())
        self.assertEqual(
            response.context["current_event"],
            event,
            "the rendered event is not the requested event",
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed("booking/event/event.html")
        mock_has_perm.assert_any_call(user, "booking.view_event", event)
