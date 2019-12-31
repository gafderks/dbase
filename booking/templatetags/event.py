from django import template

register = template.Library()


@register.filter(name="may_edit")
def may_edit(event, user):
    return event.user_may_edit(user)
