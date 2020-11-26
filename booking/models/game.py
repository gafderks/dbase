from django.contrib.auth import get_user_model
from django.db import models, transaction
from django.db.models.signals import pre_delete, pre_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _
from rules.contrib.models import RulesModel

from booking import rules
from booking.models import PartOfDay, Event
from users.models import Group
from users.models.user import get_sentinel_user


class Game(RulesModel):
    creator = models.ForeignKey(
        get_user_model(),
        # The receiver "_user_delete" replaces the creator with a sentinel user in all
        #  related games before deleting a user to ensure that the game is still
        #  associated to the group.
        on_delete=models.DO_NOTHING,
        verbose_name=_("creator"),
        related_name="games",
        editable=False,
    )
    name = models.CharField(verbose_name=_("Game name"), max_length=250)
    day = models.DateField(
        verbose_name=_("day"), help_text=_("On what day are the materials needed?")
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.CASCADE,
        verbose_name=_("group"),
    )
    event = models.ForeignKey(Event, on_delete=models.CASCADE, verbose_name=_("event"))
    part_of_day = models.CharField(
        verbose_name=_("daypart"),
        max_length=2,
        choices=PartOfDay.PART_OF_DAY_CHOICES,
        default=PartOfDay.MORNING,
        help_text=_("At what daypart are the materials needed?"),
    )
    location = models.CharField(
        verbose_name=_("location"),
        max_length=250,
        null=True,
        blank=True,
        help_text=_(
            "Where do you need the materials for this game to be delivered? This "
            "defaults to the location of the part of day."
        ),
    )
    order = models.PositiveIntegerField(
        verbose_name=_("order"),
        help_text=_("Defines an ordering for the games within a day(part)"),
        editable=False,
        default=0,
    )

    class Meta:
        verbose_name = _("game")
        verbose_name_plural = _("games")
        ordering = ["day", "part_of_day", "order"]
        default_permissions = []  # Removed default permissions as we don't check them
        rules_permissions = {
            "change": rules.change_game,
            "book_on": rules.book_on_game,
            "add_group": rules.add_game_to_group,
        }

    def __str__(self):
        return self.name

    @property
    def _siblings(self):
        return Game.objects.filter(
            day=self.day,
            part_of_day=self.part_of_day,
            group=self.group,
            event=self.event,
        )

    @property
    def previous(self):
        """
        Returns the Game that goes before this game in order.
        :return Game: previous Game
        """
        return self._siblings.filter(order__lt=self.order).last()

    @property
    def next(self):
        """
        Returns the Game that goes after this game in order.
        :return Game: next Game
        """
        return self._siblings.filter(order__gt=self.order).first()

    def swap(self, replacement):
        """
        Swaps the order of the supplied Game and this Game.
        :param Game replacement: Game for this Game to swap order with
        :return: None
        """
        with transaction.atomic():
            self_order, replacement_order = self.order, replacement.order
            self.order = replacement_order
            replacement.order = self_order
            self.save()
            replacement.save()

    swap.alters_data = True

    def up(self):
        """
        Move Game up one position.
        :return: None
        """
        previous = self.previous
        if previous:
            self.swap(previous)

    up.alters_data = True

    def down(self):
        """
        Move Game down one position.
        :return: None
        """
        _next = self.next
        if _next:
            self.swap(_next)

    down.alters_data = True

    @property
    def form(self):
        from booking.forms import GameForm

        return GameForm(instance=self, auto_id="id_game_%s_" + str(self.id))

    @property
    def booking_form(self):
        from booking.forms import BookingForm

        return BookingForm(
            initial={"game": self}, auto_id="id_game_booking_%s_" + str(self.id)
        )


@receiver(pre_save, sender=Game)
def _game_manage_order(sender, instance, **kwargs):
    """
    If a game is added newly or the part of day of the game has been changed,
    we change the order of the game such that it is the last sibling.
    :param Game sender:
    :param Game instance:
    :param kwargs:
    :return: None
    """

    def append_order(game):
        """
        Returns the order for appending a game to a day part.
        :param Game game: instance
        :return int: the order for appending
        """
        last_sibling = game._siblings.last()
        if last_sibling:
            return last_sibling.order + 1
        else:
            return 1

    try:
        current_game = sender.objects.get(pk=instance.pk)
    except sender.DoesNotExist:
        # Game is new
        instance.order = append_order(instance)
    else:
        if not current_game.part_of_day == instance.part_of_day:
            # The part of day of the game has been changed
            instance.order = append_order(instance)
        else:
            pass  # Keep game order as-is


@receiver(pre_delete, sender=get_user_model(), dispatch_uid="user_delete_signal_game")
def _user_delete(sender, instance, using, **kwargs):
    """
    Changes games of a user that gets deleted such that the creator becomes a
    sentinel user associated to the same group.
    """
    Game.objects.filter(creator=instance).update(
        creator=get_sentinel_user(instance.group)
    )
