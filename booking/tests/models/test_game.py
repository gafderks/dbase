from django.contrib.auth import get_user_model
from django.test import TestCase

from booking.models import Game
from booking.tests.factories import GameFactory
from users.tests.factories import UserFactory


class GameModelTest(TestCase):
    def test_delete_user_with_games(self):
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
        num_users_before_delete = get_user_model().objects.count()
        user.delete()
        game.refresh_from_db()
        user2.delete()
        game2.refresh_from_db()
        user3.delete()
        game3.refresh_from_db()
        # User 1 and 2 should be replaced by the same sentinel user
        # User 3 should be replaced by another sentinel user
        # User count should be decreased by one as user 1 and 2 are 'merged'.
        self.assertEqual(
            get_user_model().objects.count(),
            num_users_before_delete - 1,
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
