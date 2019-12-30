from django import template
from django.contrib.auth.models import Group as Role

register = template.Library()


@register.filter(name="has_role")
def has_role(user, role_name):
    role = Role.objects.get(name=role_name)
    return role in user.groups.all()
