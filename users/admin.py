from django.contrib import admin
from django.contrib.auth.admin import (
    UserAdmin as DjangoUserAdmin,
    GroupAdmin as DjangoGroupAdmin,
)
from django.contrib.auth.models import Group as DjangoGroup
from django.utils.translation import gettext_lazy as _

from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import User, Group, Role


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    """Define admin model for custom User model with no email field."""

    def roles(self, obj):
        return ", ".join([role.name for role in obj.groups.all()])

    roles.short_description = _("roles")

    fieldsets = (
        (None, {"fields": ("email", "password", "group")}),
        (_("Personal info"), {"fields": ("first_name", "last_name")}),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    # 'is_staff',
                    "is_superuser",
                    "groups",
                    # 'user_permissions'
                )
            },
        ),
        # (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "password1",
                    "password2",
                    "first_name",
                    "last_name",
                    "group",
                    "groups",
                ),
            },
        ),
    )
    list_display = ("email", "first_name", "last_name", "group", "roles")
    search_fields = ("email", "first_name", "last_name")
    list_filter = ("group", "groups", "is_superuser", "is_active")
    ordering = ("email",)

    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = User


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ("name", "type")
    list_filter = ("type",)


# Rename Django Groups to Roles for distinguishing from custom Group definition
admin.site.unregister(DjangoGroup)
admin.site.register(Role, DjangoGroupAdmin)
