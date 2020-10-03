from django import template
from django.contrib.auth.models import Group as Role

register = template.Library()


@register.filter(name="has_role")
def has_role(user, role_name):
    try:
        role = Role.objects.get(name=role_name)
        return role in user.groups.all()
    except Role.DoesNotExist:
        # If a role does not exist, a user cannot have it
        return False
