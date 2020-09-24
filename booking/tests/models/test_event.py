from django.test import TestCase

from booking.models import Booking, Game, Event
from booking.tests.factories import EventFactory, BookingFactory


class EventModelTest(TestCase):
    def test_delete_event_no_leftovers(self):
        event = EventFactory()
        booking = BookingFactory(game__event=event)
        self.assertEqual(Event.objects.count(), 1, "not one event was created")
        self.assertEqual(Game.objects.count(), 1, "not one game was created")
        self.assertEqual(Booking.objects.count(), 1, "not one booking was created")
        event.delete()
        self.assertEqual(Event.objects.count(), 0, "event was not deleted")
        self.assertEqual(Game.objects.count(), 0, "game was not deleted")
        self.assertEqual(Booking.objects.count(), 0, "booking was not deleted")
