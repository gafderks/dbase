from django.db import models
from django.utils.translation import gettext_lazy as _

from booking.models import Material


class MaterialAlias(models.Model):
    name = models.CharField(
        verbose_name=_("name"),
        max_length=150,
        unique=True,
        help_text=_(
            'Alias for the material, e.g. aliases for "stormbaan" are "Kelly" and '
            '"Rambler".'
        ),
    )
    material = models.ForeignKey(
        Material,
        on_delete=models.DO_NOTHING,
        verbose_name=_("material"),
        related_name="aliases",
    )

    class Meta:
        verbose_name = _("material alias")
        verbose_name_plural = _("material aliases")

    def __str__(self):
        return self.name
