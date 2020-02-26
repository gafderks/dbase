from django.db import models
from django.utils.translation import gettext_lazy as _


class Location(models.Model):
    name = models.CharField(verbose_name=_("name"), max_length=150, unique=True)

    class Meta:
        verbose_name = _("location")
        verbose_name_plural = _("locations")

    def __str__(self):
        return self.name
