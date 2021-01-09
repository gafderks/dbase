from django.test import TestCase
from django.urls import reverse

from booking.tests.factories import GameFactory, BookingFactory


class EventExcelViewTest(TestCase):
    def test_can_export_excel(self):
        game = GameFactory()
        bookings = BookingFactory.create_batch(5, game=game)
        self.client.force_login(game.creator)
        response = self.client.get(
            reverse(
                "booking:api:excel_event",
                kwargs={
                    "event_slug": game.event.slug,
                    "group_slug": game.creator.group.slug,
                },
            )
        )
        self.assertEqual(
            response.content_type,
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
