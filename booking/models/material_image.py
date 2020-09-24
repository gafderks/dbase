from django.db import models
from django.utils.translation import gettext_lazy as _
from adminsortable.models import SortableMixin
from sorl.thumbnail import ImageField

from booking.models import Material


class MaterialImage(SortableMixin):
    image = ImageField(upload_to="materials", verbose_name=_("image"))
    material = models.ForeignKey(
        Material,
        related_name="images",
        on_delete=models.CASCADE,
        verbose_name=_("material"),
    )
    image_order = models.PositiveIntegerField(default=0, editable=False, db_index=True)

    class Meta:
        verbose_name = _("material image")
        verbose_name_plural = _("material images")
        ordering = ["image_order"]
