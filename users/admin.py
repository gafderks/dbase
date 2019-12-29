from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.utils.translation import gettext, gettext_lazy as _

from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import User, Group


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    """Define admin model for custom User model with no email field."""

    fieldsets = (
        (None, {'fields': ('email', 'password', 'group')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
        # (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'group'),
        }),
    )
    list_display = ('email', 'first_name', 'last_name', 'group', 'is_staff')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)

    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = User


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('name',)
