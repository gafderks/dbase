from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _
from rules.contrib.models import RulesModel

from booking import rules
from booking.models import Game, Material


class Booking(RulesModel):
    requester = models.ForeignKey(
        get_user_model(),
        on_delete=models.DO_NOTHING,
        verbose_name=_("requester"),
        related_name="bookings",
        editable=False,
    )
    game = models.ForeignKey(
        Game,
        on_delete=models.CASCADE,
        verbose_name=_("game"),
        related_name="bookings",
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
            ("change_other_groups_bookings", "Can change bookings of other groups"),
            ("view_others_groups_bookings", "Can view bookings of other groups"),
        ]
        default_permissions = []  # Removed default permissions as we don't check them
        rules_permissions = {"change": rules.change_booking}

    def __str__(self):
        if self.material:
            return self.material.name
        if self.custom_material:
            return self.custom_material
        else:
            return str(_("Unspecified material"))  # Should actually never be the shown

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
