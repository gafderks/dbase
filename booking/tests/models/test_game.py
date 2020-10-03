from django.contrib.auth import get_user_model
from django.test import TestCase

from booking.models import Game
from booking.tests.factories import GameFactory, EventFactory
from users.tests.factories import UserFactory, GroupFactory


def _get_sibling_games(n=5, part_of_day="AF", **kwargs):
    if "event" not in kwargs.keys():
        kwargs["event"] = EventFactory()
    if "group" not in kwargs.keys():
        kwargs["group"] = GroupFactory()
    return GameFactory.create_batch(
        n,
        day=kwargs["event"].event_start,
        part_of_day=part_of_day,
        **kwargs,
    )


class GameModelTest(TestCase):
    def _assert_game_order(self, games, order, msg=None):
        # order = 3, 0, 2, 1
        # games = [game.2, game.4, game.3, game.1]
        assert len(games) == len(order) == len(set(order))
        # Get the game that is first in order
        game = games[order[0]]
        for i in order[1:]:
            # The index of the next game should match the next number in the order array
            self.assertEqual(games.index(game.next), i, msg)
            game = game.next
            if game.next:
                # Check if previous works as well
                self.assertEqual(game.previous, game.next.previous.previous)

    def test_new_game_appended(self):
        games = _get_sibling_games(10)
        for i in range(1, 10):
            self.assertGreater(
                games[i].order, games[i - 1].order, "insertion order is not saved"
            )

    def test_game_change_part_of_day_appended(self):
        morning_games = _get_sibling_games(4, part_of_day="MO")
        afternoon_games = _get_sibling_games(
            4,
            part_of_day="AF",
            group=morning_games[0].group,
            event=morning_games[0].event,
        )
        games = [
            *morning_games,
            *afternoon_games,
        ]
        # move second game to afternoon
        games[1].part_of_day = "AF"
        games[1].save()
        # game should be last in afternoon
        self.assertIsNone(games[1].next, "game was not last of siblings")
        # move game back to morning
        games[1].part_of_day = "MO"
        games[1].save()
        self.assertIsNone(games[1].next, "game was not last of siblings")

    def test_game_move(self):
        games = _get_sibling_games(6)

        def refresh_games():
            for game in games:
                game.refresh_from_db()

        self._assert_game_order(games, [0, 1, 2, 3, 4, 5], msg="insertion order wrong")

        # We want to create order [2, 3, 0, 5, 4, 1]
        # Move game 1 to the end (4 times down)
        for i in range(10):
            games[1].down()
            refresh_games()
        self._assert_game_order(games, [0, 2, 3, 4, 5, 1], msg="down order wrong")
        # Swap game 0 and game 2
        games[2].swap(games[0])
        self._assert_game_order(games, [2, 0, 3, 4, 5, 1], msg="swapping order wrong")
        # Move game 3 one up
        games[3].up()
        self._assert_game_order(games, [2, 3, 0, 4, 5, 1], msg="up order wrong")
        # Swap game 4 and 5
        games[4].swap(games[5])
        self._assert_game_order(games, [2, 3, 0, 5, 4, 1], msg="swapping order wrong")

    def test_delete_user_with_games_keeps_games(self):
        # User 1 and 2 are from the same group
        # User 3 is from a different group
        user = UserFactory()
        game = GameFactory(creator=user)
        group = user.group
        user2 = UserFactory(group=group)
        game2 = GameFactory(creator=user2)
        user3 = UserFactory()
        game3 = GameFactory(creator=user3)
        self.assertEqual(
            group,
            game.creator.group,
            "game1 not associated with creator group",
        )
        self.assertEqual(
            group,
            game2.creator.group,
            "game2 not associated with creator group",
        )
        self.assertNotEqual(
            game.creator,
            game2.creator,
            "games are associated with same creator",
        )
        user.delete()
        game.refresh_from_db()
        user2.delete()
        game2.refresh_from_db()
        user3.delete()
        game3.refresh_from_db()
        # User 1 and 2 should be replaced by the same sentinel user
        # User 3 should be replaced by another sentinel user
        # User count should be 2 now as user 1 and 2 are 'merged'.
        self.assertEqual(
            get_user_model().objects.count(),
            2,
            "users were not replaced",
        )
        self.assertEqual(Game.objects.count(), 3, "game was deleted")
        self.assertEqual(group, game.creator.group, "game1 changed group")
        self.assertEqual(group, game2.creator.group, "game2 changed group")
        self.assertEqual(
            game.creator.email,
            f"deleted_user@{group}",
            "creator was not replaced with sentinel user",
        )
        self.assertEqual(
            game2.creator.email,
            f"deleted_user@{group}",
            "creator was not replaced with sentinel user",
        )
        self.assertEqual(
            game.creator,
            game2.creator,
            "different sentinel users were used for the same group",
        )
        self.assertNotEqual(
            game.creator,
            game3.creator,
            "same sentinel user was used for different groups",
        )
