from datetime import timedelta

from django.test import TestCase, RequestFactory
from django.views import View

from booking.mixins import NavigationMixin, BookingPageMixin
from booking.tests.factories import BookingFactory, EventFactory
from tests.utils import english
from users.models import Group
from users.tests.factories import UserFactory, GroupFactory


class TestNavigationMixin(TestCase):
    class DummyView(NavigationMixin, View):
        pass

    def test_get_context_data_empty(self):
        request = RequestFactory().get("/non-existent")
        request.user = UserFactory()
        context = self.DummyView(request=request).get_context_data()

        self.assertEqual(len(context["events"]), 0, "there should be no events")
        self.assertEqual(
            context["current_event"], None, "there should be no current event"
        )
        self.assertEqual(context["typeahead_thumbprint"], "never")

    def test_get_context_data_not_empty(self):
        latest_event = EventFactory()
        other_event = EventFactory(event_end=latest_event.event_end - timedelta(5))
        booking = BookingFactory(game__event=latest_event)  # Creates a material

        request = RequestFactory().get("/non-existent")
        request.user = UserFactory()
        context = self.DummyView(request=request).get_context_data()

        self.assertEqual(list(context["events"]), [latest_event, other_event])
        self.assertEqual(context["current_event"], latest_event)
        self.assertEqual(
            context["typeahead_thumbprint"], booking.material.last_modified.isoformat()
        )


class TestBookingPageMixin(TestCase):
    class DummyView(BookingPageMixin, View):
        pass

    @english
    def test_get_context_data(self):
        groups = GroupFactory.create_batch(5, type=Group.GroupType.GROUP)
        commissions = GroupFactory.create_batch(5, type=Group.GroupType.COMMISSION)
        user = UserFactory(group=groups[0])

        request = RequestFactory().get("/non-existent")
        request.user = user
        context = self.DummyView(request=request).get_context_data()

        for group in groups:
            self.assertTrue(group in context["groups"])
        for commission in commissions:
            self.assertTrue(commission in context["commissions"])

        self.assertEqual(
            context["parts_of_day"],
            [
                ("DA", "Day"),
                ("MO", "Morning"),
                ("AF", "Afternoon"),
                ("EV", "Evening"),
                ("NI", "Night"),
            ],
        )

        for key in ["events", "current_event", "typeahead_thumbprint"]:
            self.assertTrue(
                key in context,
                f"{key} should be part of context through super class NavigationMixin",
            )
