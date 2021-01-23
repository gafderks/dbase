from django import template

register = template.Library()


@register.filter
def multiply(string, times):
    return string * times
