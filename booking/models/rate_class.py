from django.db import models
from django.utils.translation import gettext_lazy as _

from djmoney.models.fields import MoneyField
from djmoney.models.validators import MinMoneyValidator


class RateClass(models.Model):
    name = models.CharField(verbose_name=_("name"), max_length=150, unique=True)
    description = models.CharField(
        verbose_name=_("description"), max_length=250, blank=True
    )
    rate = MoneyField(
        verbose_name=_("rate"),
        decimal_places=2,
        max_digits=6,
        default_currency="EUR",
        validators=[MinMoneyValidator(0)],
    )

    class Meta:
        verbose_name = _("rate class")
        verbose_name_plural = _("rate classes")

    def __str__(self):
        return self.name
