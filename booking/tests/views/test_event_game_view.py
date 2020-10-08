from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse

from booking.tests.factories import EventFactory, GameFactory
from users.tests.factories import UserFactory, GroupFactory


class EventGameViewTest(TestCase):

    ####################################################################################
    # Tests for EventGameView.dispatch
    ####################################################################################

    def test_game_view(self):
        event = EventFactory()
        user = UserFactory()
        self.client.force_login(user)
        response = self.client.get(
            reverse(
                "booking:event_games_group",
                kwargs={"event_slug": event.slug, "group_slug": user.group.slug},
            ),
        )
        self.assertTemplateUsed(response, "booking/event/game-view.html")
        self.assertTemplateNotUsed(response, "booking/event/list-view.html")

    def test_redirect_listview_group_all(self):
        event = EventFactory()
        self.client.force_login(UserFactory())
        response = self.client.get(
            reverse(
                "booking:event_games_group",
                kwargs={"event_slug": event.slug, "group_slug": "all"},
            ),
            follow=True,
        )
        self.assertTemplateUsed(response, "booking/event/list-view.html")
        self.assertTemplateNotUsed(response, "booking/event/game-view.html")

    ####################################################################################
    # Tests for EventGameView.get_context_data
    ####################################################################################

    def test_game_in_context(self):
        game = GameFactory()
        self.client.force_login(game.creator)
        response = self.client.get(
            reverse(
                "booking:event_games_group",
                kwargs={
                    "event_slug": game.event.slug,
                    "group_slug": game.creator.group.slug,
                },
            ),
        )
        self.assertIn(
            game,
            response.context["games"][game.day][game.part_of_day],
            "game is not part of context",
        )

    def test_other_event_game_not_in_context(self):
        game = GameFactory()
        other_game = GameFactory(
            creator=game.creator,
            event__event_start=game.event.event_start,
            event__event_end=game.event.event_end,
        )  # has other event but with same dates
        self.client.force_login(game.creator)
        response = self.client.get(
            reverse(
                "booking:event_games_group",
                kwargs={
                    "event_slug": game.event.slug,
                    "group_slug": game.creator.group.slug,
                },
            ),
        )
        self.assertNotIn(
            other_game,
            response.context["games"][other_game.day][other_game.part_of_day],
            "game from other event is part of context",
        )

    @patch("django.contrib.auth.backends.ModelBackend.has_perm")
    def test_all_games_from_same_group(self, mock_has_perm):
        mock_has_perm.return_value = True

        event = EventFactory()
        user = UserFactory()
        other_group = GroupFactory()
        games_user_group = GameFactory.create_batch(
            3, group=user.group, creator=user, event=event
        )
        games_other_group = GameFactory.create_batch(
            3, group=other_group, creator=user, event=event
        )
        self.client.force_login(user)
        response = self.client.get(
            reverse(
                "booking:event_games_group",
                kwargs={
                    "event_slug": event.slug,
                    "group_slug": user.group.slug,
                },
            ),
        )
        self.assertEqual(response.context["current_group"], user.group)
        for game in games_other_group:
            self.assertNotIn(
                game,
                response.context["games"][game.day][game.part_of_day],
                "game from other group is part of context",
            )
        for game in games_user_group:
            self.assertIn(
                game,
                response.context["games"][game.day][game.part_of_day],
                "game from own group is not part of context",
            )
        # Now check with reversed groups
        response = self.client.get(
            reverse(
                "booking:event_games_group",
                kwargs={
                    "event_slug": event.slug,
                    "group_slug": other_group.slug,
                },
            ),
        )
        self.assertEqual(response.context["current_group"], other_group)
        for game in games_other_group:
            self.assertIn(
                game,
                response.context["games"][game.day][game.part_of_day],
                "game from other group is not part of context",
            )
        for game in games_user_group:
            self.assertNotIn(
                game,
                response.context["games"][game.day][game.part_of_day],
                "game from own group is part of context",
            )
        mock_has_perm.assert_any_call(user, "booking.view_others_groups_bookings", None)
