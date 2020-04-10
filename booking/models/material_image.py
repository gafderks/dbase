from django.db import models
from django.utils.translation import gettext_lazy as _
from sorl.thumbnail import ImageField

from booking.models import Material


class MaterialImage(models.Model):
    image = ImageField(upload_to="materials", verbose_name=_("image"))
    material = models.ForeignKey(
        Material,
        related_name="images",
        on_delete=models.DO_NOTHING,
        verbose_name=_("material"),
    )

    class Meta:
        verbose_name = _("material image")
        verbose_name_plural = _("material images")
