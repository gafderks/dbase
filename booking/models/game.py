from django.db import models, transaction
from django.contrib.auth import get_user_model
from django.forms import model_to_dict
from django.utils.translation import gettext_lazy as _

from booking.models import PartOfDay, Event
from users.models import Group


class Game(models.Model):
    creator = models.ForeignKey(
        get_user_model(),
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
        Group, on_delete=models.DO_NOTHING, verbose_name=_("group")
    )
    event = models.ForeignKey(Event, on_delete=models.CASCADE, verbose_name=_("event"))
    part_of_day = models.CharField(
        verbose_name=_("part of day"),
        max_length=2,
        choices=PartOfDay.PART_OF_DAY_CHOICES,
        default=PartOfDay.MORNING,
        help_text=_("At what part of the day are the materials needed?"),
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
        help_text=_("Defines an ordering for the games within a day/part of day"),
        editable=False,
        default=0,
    )

    class Meta:
        verbose_name = _("game")
        verbose_name_plural = _("games")
        ordering = ["day", "part_of_day", "order"]

    def __str__(self):
        return self.name

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__initial = self._dict

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
        return self._siblings.filter(order__lt=self.order).last()

    @property
    def next(self):
        return self._siblings.filter(order__gt=self.order).first()

    def save(self, *args, **kwargs):
        # If the game is new (order=0) or it has changed part_of_day we put it last
        if self.order == 0 or self.part_of_day != self.__initial["part_of_day"]:
            last_sibling = self._siblings.last()
            if last_sibling:
                self.order = last_sibling.order + 1
            else:
                self.order = 1

        super().save(*args, **kwargs)
        self.__initial = self._dict

    @property
    def _dict(self):
        return model_to_dict(self, fields=[field.name for field in self._meta.fields])

    def swap(self, other):
        with transaction.atomic():
            self_order, other_order = (getattr(self, "order"), getattr(other, "order"))
            setattr(self, "order", other_order)
            setattr(other, "order", self_order)
            self.save()
            other.save()

    def up(self):
        previous = self.previous
        if previous:
            self.swap(previous)

    def down(self):
        _next = self.next
        if _next:
            self.swap(_next)

    def user_may_edit(self, user):
        if not self.event.user_may_edit(user):
            return False
        if self.group != user.group:
            if not user.has_perm("booking.can_edit_others_groups_bookings"):
                return False
        return True

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
