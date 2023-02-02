from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse

from booking.tests.factories import GameFactory, BookingFactory
from users.tests.factories import UserFactory


class EventListViewTest(TestCase):
    ####################################################################################
    # Tests for EventListView.get_context_data
    ####################################################################################

    def test_lists_and_bookings_in_context(self):
        game = GameFactory()
        bookings = BookingFactory.create_batch(5, game=game)
        self.client.force_login(game.creator)
        response = self.client.get(
            reverse(
                "booking:event_list_group",
                kwargs={
                    "event_slug": game.event.slug,
                    "group_slug": game.creator.group.slug,
                },
            ),
        )
        # There are no ListViewFilters, hence all bookings should be part of the
        #  leftover ListView.
        lv, lv_bookings = response.context["list_views"][game.day][game.part_of_day][0]
        self.assertCountEqual(
            bookings, lv_bookings, "not all bookings are part of the leftover listview"
        )
        self.assertTemplateUsed(response, "booking/event/list-view.html")

    # Tests BookingFilter
    def test_filtered_bookings_not_in_context(self):
        game = GameFactory()
        bookings_gm = BookingFactory.create_batch(3, game=game, material__gm=True)
        bookings_no_gm = BookingFactory.create_batch(2, game=game, material__gm=False)
        self.client.force_login(game.creator)
        response = self.client.get(
            reverse(
                "booking:event_list_group",
                kwargs={
                    "event_slug": game.event.slug,
                    "group_slug": game.creator.group.slug,
                },
            )
            + "?gm=True",
        )
        # There are no ListViewFilters, hence all bookings should be part of the
        #  leftover ListView.
        lv, lv_bookings = response.context["list_views"][game.day][game.part_of_day][0]
        for booking in bookings_gm:
            self.assertIn(booking, lv_bookings, "filtered booking is not in listview")
        for booking in bookings_no_gm:
            self.assertNotIn(
                booking, lv_bookings, "excluded booking is part of listview"
            )
        self.assertTemplateUsed(response, "booking/event/list-view.html")

    @patch("django.contrib.auth.backends.ModelBackend.has_perm")
    def test_bookings_from_different_groups_combined_in_group_all(self, mock_has_perm):
        mock_has_perm.return_value = True
        # Create two bookings and games at the same moment and for the same event, but
        #  with a different group.
        booking1 = BookingFactory()
        booking2 = BookingFactory(
            game__event=booking1.game.event,
            game__day=booking1.game.day,
            game__part_of_day=booking1.game.part_of_day,
        )
        self.assertNotEqual(booking1.game.group, booking2.game.group)
        bookings = [booking1, booking2]
        user = UserFactory()
        self.client.force_login(user)
        response = self.client.get(
            reverse(
                "booking:event_list_group",
                kwargs={
                    "event_slug": booking1.game.event.slug,
                    "group_slug": "all",
                },
            )
        )
        # There are no ListViewFilters, hence all bookings should be part of the
        #  leftover ListView.
        lv, lv_bookings = response.context["list_views"][booking1.game.day][
            booking1.game.part_of_day
        ][0]
        self.assertCountEqual(
            lv_bookings,
            bookings,
            "bookings for different groups are not combined in the list view",
        )
        self.assertTemplateUsed(response, "booking/event/list-view.html")
        mock_has_perm.assert_any_call(user, "booking.view_others_groups_bookings", None)
