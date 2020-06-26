from django.db import models
from django.utils.translation import gettext_lazy as _
from ckeditor.fields import RichTextField

from booking.models import Category, Location, RateClass


class Material(models.Model):
    name = models.CharField(verbose_name=_("name"), max_length=150, unique=True)
    description = RichTextField(
        verbose_name=_("description"),
        blank=True,
        config_name="basic_ckeditor",
        help_text=_(
            "Additional information about the material. Displayed in the shop."
        ),
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
    stock_value = models.FloatField(
        verbose_name=_("stock value"),
        null=True,
        blank=True,
        help_text=_("How many exemplars are there of this material?"),
    )
    stock_unit = models.CharField(
        verbose_name=_("stock unit"),
        max_length=150,
        blank=True,
        help_text=_("Specify a unit for the stock. E.g. meters."),
    )
    last_modified = models.DateTimeField(auto_now=True, editable=False)

    class Meta:
        verbose_name = _("material")
        verbose_name_plural = _("materials")
        get_latest_by = "last_modified"

    def __str__(self):
        return self.name

    @property
    def stock(self):
        return " ".join(
            [
                str(val)[:-2] if str(val).endswith(".0") else str(val)  # Remove .0
                for val in [self.stock_value, self.stock_unit]  # Concat value and unit
                if val is not None
            ]
        )

    stock.fget.short_description = _("stock")

    @staticmethod
    def last_modification():
        if Material.objects.count() == 0:
            return None
        return Material.objects.latest().last_modified
