from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _

from booking.models import Game, Material


class Booking(models.Model):
    requester = models.ForeignKey(
        get_user_model(),
        on_delete=models.DO_NOTHING,
        verbose_name=_("requester"),
        related_name="bookings",
        editable=False,
    )
    game = models.ForeignKey(
        Game, on_delete=models.CASCADE, verbose_name=_("game"), related_name="bookings",
    )
    material = models.ForeignKey(
        Material,
        on_delete=models.DO_NOTHING,
        verbose_name=_("material"),
        related_name="bookings",
        null=True,
        blank=True,
    )
    custom_material = models.CharField(
        max_length=150, verbose_name=_("custom material"), null=True, blank=True
    )
    workweek = models.BooleanField(verbose_name=_("workweek"))
    comment = models.CharField(
        max_length=250,
        blank=True,
        null=True,
        verbose_name=_("comment"),
        help_text=_("E.g. for food: when and where do you need it?"),
    )
    amount = models.CharField(max_length=150, verbose_name=_("amount"))

    class Meta:
        verbose_name = _("booking")
        verbose_name_plural = _("bookings")
        permissions = [
            ("can_change_other_groups_bookings", "Can change bookings of other groups"),
            ("can_view_others_groups_bookings", "Can view bookings of other groups"),
        ]
        default_permissions = []  # Removed default permissions as we don't check them

    def __str__(self):
        return self.material.name if self.material else self.custom_material

    def user_may_edit(self, user):
        if not self.game.user_may_edit(user):
            return False
        return True

    @property
    def form(self):
        from booking.forms import BookingForm

        return BookingForm(instance=self, auto_id="id_booking_%s_" + str(self.id))

    @property
    def form_with_game(self):
        from booking.forms import BookingForm

        form = BookingForm(instance=self, auto_id="id_booking_%s_" + str(self.id))
        form.helper.form_action += "?include_game=True"
        return form

    @property
    def form_with_group(self):
        from booking.forms import BookingForm

        form = BookingForm(instance=self, auto_id="id_booking_%s_" + str(self.id))
        form.helper.form_action += "?include_game=True&include_group=True"
        return form

    @property
    def display_category(self):
        if self.material is None:
            return _("Custom material")
        if self.material.categories.exists():
            return str(self.material.categories.first())
        else:
            return ""
