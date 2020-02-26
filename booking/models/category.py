from django.db import models
from django.utils.translation import gettext_lazy as _


class Category(models.Model):
    name = models.CharField(verbose_name=_("name"), max_length=150, unique=True)
    description = models.CharField(
        verbose_name=_("description"), max_length=250, blank=True
    )

    class Meta:
        verbose_name = _("category")
        verbose_name_plural = _("categories")

    def __str__(self):
        return self.name
