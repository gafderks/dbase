from django.db import models
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from booking.models import Material


class MaterialImage(models.Model):
    image = models.ImageField(upload_to="materials", verbose_name=_("image"))
    material = models.ForeignKey(
        Material,
        related_name="images",
        on_delete=models.DO_NOTHING,
        verbose_name=_("material"),
    )

    def image_tag(self):
        return mark_safe(
            '<img src="{}" width="150" height="150" />'.format(self.image.url)
        )

    image_tag.short_description = "Preview"

    class Meta:
        verbose_name = _("material image")
        verbose_name_plural = _("material images")
