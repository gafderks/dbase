from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse

from booking.tests.factories import EventFactory, MaterialFactory
from tests.utils import english
from users.tests.factories import UserFactory


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
        for group_slug in ["all", users[1].group.slug]:
            response = self.client.get(
                reverse(
                    "booking:event_games_group",
                    kwargs={"event_slug": event.slug, "group_slug": group_slug},
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
        for group_slug, group in zip(
            ["all", users[1].group.slug], [None, users[1].group]
        ):
            response = self.client.get(
                reverse(
                    "booking:event_games_group",
                    kwargs={
                        "event_slug": event.slug,
                        "group_slug": group_slug,
                    },
                ),
                follow=True,
            )
            self.assertEqual(
                response.context["current_group"],
                group,
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

    ####################################################################################
    # Tests for BookingMixin.get_context_data with typeahead thumbnail
    ####################################################################################

    def test_typeahead_thumbprint_not_none(self):
        materials = MaterialFactory.create_batch(3)
        last_material = MaterialFactory()
        self.assertNotEqual(materials[0].last_modified, last_material.last_modified)
        event = EventFactory()
        self.client.force_login(UserFactory())
        response = self.client.get(event.get_absolute_url())
        self.assertEqual(
            response.context["typeahead_thumbprint"],
            last_material.last_modified.isoformat(),
            "typeahead thumbprint is not correct",
        )

    def test_typeahead_thumbprint_never(self):
        event = EventFactory()
        self.client.force_login(UserFactory())
        response = self.client.get(event.get_absolute_url())
        self.assertEqual(
            response.context["typeahead_thumbprint"],
            "never",
            "typeahead thumbprint is not correct",
        )
