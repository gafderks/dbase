from django.contrib.auth.models import Group as DjangoGroup
from django.utils.translation import gettext_lazy as _


class Role(DjangoGroup):
    """Rename Django Groups to Roles for distinguishing from custom Group definition"""

    class Meta:
        proxy = True
        app_label = "auth"
        verbose_name = _("role")
        verbose_name_plural = _("roles")
