from django import template

register = template.Library()


@register.simple_tag(takes_context=True)
def param_replace(context, **kwargs):
    """
    Replace GET parameters in the current URL while leaving the other parameters intact.
    Setting a parameter falsey removes it from the query string.

    :param dict context: request context
    :param dict kwargs: key, value dict
    :return str: updated query string
    """
    get_variable_dict = context["request"].GET.copy()
    # Set variables for which a value is given
    for key, value in kwargs.items():
        get_variable_dict[key] = value
    # Remove variables for which the value is falsey
    for key in [key for key, value in get_variable_dict.items() if not value]:
        del get_variable_dict[key]
    return get_variable_dict.urlencode()
