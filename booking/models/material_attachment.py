from django.db import models
from django.utils.translation import gettext_lazy as _
from adminsortable.models import SortableMixin

from booking.models import Material


class MaterialAttachment(SortableMixin):
    attachment = models.FileField(
        upload_to="material-attachments", verbose_name=_("attachment")
    )
    material = models.ForeignKey(
        Material,
        related_name="attachments",
        on_delete=models.DO_NOTHING,
        verbose_name=_("material"),
    )
    attachment_order = models.PositiveIntegerField(
        default=0, editable=False, db_index=True
    )

    class Meta:
        verbose_name = _("material attachment")
        verbose_name_plural = _("material attachments")
        ordering = ["attachment_order"]
