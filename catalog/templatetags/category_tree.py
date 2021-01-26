from django import template

register = template.Library()


@register.filter
def multiply(string, times):
    """
    Repeats a string a given number of times.
    :param str string: given string
    :param number times: number of repeats
    :return str: repeated string
    """
    return string * times


@register.filter
def descendant_pks(category):
    """
    Returns a list of the primary keys of the descendants of the given category,
    not including the pk of the category itself.
    :param Category category: category
    :return [number]: list of the primary keys
    """
    return [str(desc.pk) for desc in category.get_descendants(include_self=False)]
