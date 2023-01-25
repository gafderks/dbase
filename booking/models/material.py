from ckeditor.fields import RichTextField
from django.conf import settings
from django.db import models
from django.db.models.functions import Lower
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from mptt.fields import TreeManyToManyField

from booking.models import Category, Location, RateClass


def format_stock_value(val: float) -> str:
    """
    Removes trailing zeroes and after that any trailing dot.
    """
    return "{:.2f}".format(val).rstrip("0").rstrip(".")


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
    categories = TreeManyToManyField(
        Category, related_name="materials", verbose_name=_("categories")
    )
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
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name=_("location"),
        help_text=_("Where can this material be found?"),
        related_name="materials",
    )
    rate_class = models.ForeignKey(
        RateClass,
        on_delete=models.SET_NULL,
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
    lendable_stock_value = models.FloatField(
        verbose_name=_("lendable stock value"),
        null=True,
        blank=True,
        help_text=_("How many exemplars of this materials are lendable?"),
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
        ordering = [Lower("name")]

    def __str__(self):
        return self.name

    @property
    def stock(self):
        """
        Returns a human readable representation of the stock
        """
        parts = []
        if self.stock_value is not None:
            parts.append(format_stock_value(self.stock_value))
        if len(parts) and self.stock_unit:
            parts.append(self.stock_unit)
        return " ".join(parts).strip()

    stock.fget.short_description = _("stock")

    @property
    def lendable_stock(self):
        """
        Returns a human readable representation of the lendable stock
        """
        parts = []
        if self.lendable_stock_value is not None:
            parts.append(format_stock_value(self.lendable_stock_value))
        elif self.stock_value:
            parts.append(format_stock_value(self.stock_value))
        if len(parts) and self.stock_unit:
            parts.append(self.stock_unit)
        return " ".join(parts).strip()

    lendable_stock.fget.short_description = _("lendable stock")

    @property
    def sku(self):
        return self.id + settings.SHOP_SKU_OFFSET

    @staticmethod
    def last_modification():
        try:
            return Material.objects.latest().last_modified
        except Material.DoesNotExist:
            return None

    def get_absolute_url(self):
        return reverse("catalog:material", kwargs={"pk": self.pk})

    def get_shop_url(self):
        if self.lendable and settings.SHOP_PRODUCT_URL_FORMAT:
            return settings.SHOP_PRODUCT_URL_FORMAT.format(sku=self.sku)
        else:
            return None
