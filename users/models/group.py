from django.db import models
from django.utils.translation import gettext_lazy as _


class Group(models.Model):
    name = models.CharField(max_length=250, unique=True)
    GROUP = "GR"
    COMMISSION = "CO"
    GROUP_TYPE_CHOICES = [
        (GROUP, _("Group")),
        (COMMISSION, _("Commission")),
    ]
    type = models.CharField(
        max_length=2,
        choices=GROUP_TYPE_CHOICES,
        default=COMMISSION,
        verbose_name=_("type"),
        help_text=_("What type is the group?"),
    )

    class Meta:
        verbose_name = _("group")
        verbose_name_plural = _("groups")
        ordering = ["name"]

    def __str__(self):
        return self.name
