from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.contrib.auth.models import Group as DjangoGroup, Permission
from django.db.models import Count
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
    prepopulated_fields = {"slug": ("name",)}


# Rename Django Groups to Roles for distinguishing from custom Group definition
admin.site.unregister(DjangoGroup)


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ("name", "count_permissions", "count_users")

    def get_queryset(self, request):
        qs = super(RoleAdmin, self).get_queryset(request)
        return qs.annotate(permission_count=Count("permissions"))

    def count_permissions(self, obj):
        return obj.permission_count

    def count_users(self, obj):
        return _("%(user_count)s users") % {"user_count": obj.user_set.count()}

    count_permissions.short_description = _("Number of permissions")
    count_users.short_description = _("Number of users")


@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    search_fields = ["codename"]
    list_display = ("pk", "__str__", "assigned_to")
    list_display_links = ("pk", "__str__")

    def assigned_to(self, obj):
        return ", ".join([role.name for role in obj.group_set.all()])

    assigned_to.short_description = _("assigned to")
