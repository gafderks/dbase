from django.db import models
from django.utils.translation import gettext_lazy as _


class Group(models.Model):
    name = models.CharField(max_length=250, unique=True)
    slug = models.SlugField(null=False, unique=True, help_text=_("URL short name"))

    class GroupType(models.TextChoices):
        GROUP = "GR", _("Group")
        COMMISSION = "CO", _("Commission")

    type = models.CharField(
        max_length=2,
        choices=GroupType.choices,
        default=GroupType.COMMISSION,
        verbose_name=_("type"),
        help_text=_("What type is the group?"),
    )

    class Meta:
        verbose_name = _("group")
        verbose_name_plural = _("groups")
        ordering = ["name"]

    def __str__(self):
        return self.name
