from django import template

register = template.Library()


@register.filter(name="get_item")
def get_item(dictionary, key):
    """

    :param dictionary: dict
    :param key:
    :return:
    """
    if dictionary is None:
        return None
    return dictionary.get(key, None)
