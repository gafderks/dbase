from django.db import models
from django.utils.translation import gettext_lazy as _

from booking.models import Category, Location, RateClass


class Material(models.Model):
    name = models.CharField(verbose_name=_("name"), max_length=150, unique=True)
    description = models.CharField(
        verbose_name=_("description"), max_length=250, blank=True
    )
    categories = models.ManyToManyField(Category, related_name="materials")
    gm = models.BooleanField(
        verbose_name=_("GM"), help_text=_("Is GM needed for this material?")
    )
    lendable = models.BooleanField(
        verbose_name=_("lendable"),
        default=False,
        help_text=_("Should this material be shown for lending?"),
    )
    location = models.ForeignKey(
        Location,
        on_delete=models.DO_NOTHING,
        blank=True,
        null=True,
        verbose_name=_("location"),
        help_text=_("Where can this material be found?"),
        related_name="materials",
    )
    rate_class = models.ForeignKey(
        RateClass,
        on_delete=models.DO_NOTHING,
        blank=True,
        null=True,
        verbose_name=_("rate class"),
        related_name="materials",
        help_text=_("What rate class should this material be associated with?"),
    )
    stock = models.CharField(
        verbose_name=_("stock"),
        max_length=150,
        blank=True,
        help_text=_("How many exemplars are there of this material?"),
    )

    class Meta:
        verbose_name = _("material")
        verbose_name_plural = _("materials")

    def __str__(self):
        return self.name
