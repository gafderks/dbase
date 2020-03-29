from django.db import models
from django.utils.translation import gettext_lazy as _

from booking.models import Event
from users.models import Group


class PartOfDay(models.Model):
    day = models.DateField(
        verbose_name=_("day"), help_text=_("On what day are the materials needed?")
    )
    group = models.ForeignKey(
        Group, on_delete=models.DO_NOTHING, verbose_name=_("group")
    )
    event = models.ForeignKey(Event, on_delete=models.CASCADE, verbose_name=_("event"))
    MORNING = "MO"
    AFTERNOON = "AF"
    EVENING = "EV"
    DAY = "DA"
    NIGHT = "NI"
    PART_OF_DAY_CHOICES = [
        (DAY, _("Day")),
        (MORNING, _("Morning")),
        (AFTERNOON, _("Afternoon")),
        (EVENING, _("Evening")),
        (NIGHT, _("Night")),
    ]
    part_of_day_code = models.CharField(
        verbose_name=_("daypart"),
        max_length=2,
        choices=PART_OF_DAY_CHOICES,
        default=MORNING,
        help_text=_("At what daypart are the materials needed?"),
    )
    start_time = models.TimeField(verbose_name=_("start time"), null=True)
    end_time = models.TimeField(verbose_name=_("end time"), null=True)
    location = models.CharField(
        verbose_name=_("location"),
        max_length=250,
        null=True,
        blank=True,
        help_text=_(
            "Where do you need the materials for this daypart to be delivered?"
        ),
    )

    class Meta:
        verbose_name = _("daypart")
        verbose_name_plural = _("dayparts")
        default_permissions = []  # Removed default permissions as we don't check them

    @property
    def part_of_day(self):
        part_of_day_dict = {code: trans for code, trans in self.PART_OF_DAY_CHOICES}
        return part_of_day_dict[self.part_of_day_code]

    def __str__(self):
        return "{} {}".format(self.day, self.part_of_day)
