from html import unescape
from urllib.parse import parse_qsl

from django.http import HttpRequest, QueryDict
from django.template import Context, Template
from django.test import TestCase


def get_context(query_dict):
    request = HttpRequest()
    request.GET = QueryDict(mutable=True)
    for key, value in query_dict.items():
        request.GET[key] = value
    return Context({"request": request})


class ParamReplaceTest(TestCase):
    def test_new_param(self):
        context = get_context(dict())
        template_to_render = Template(
            "{% load query_url %}" "{% param_replace abc=156 %}"
        )
        rendered_template = template_to_render.render(context)
        rendered_template = unescape(rendered_template)
        decoded_template = dict(parse_qsl(rendered_template))
        self.assertDictEqual(decoded_template, {"abc": "156"})

    def test_update_param(self):
        context = get_context({"page": "one", "abc": "113"})
        template_to_render = Template(
            "{% load query_url %}" "{% param_replace abc=4 %}"
        )
        rendered_template = template_to_render.render(context)
        rendered_template = unescape(rendered_template)
        decoded_template = dict(parse_qsl(rendered_template))
        self.assertDictEqual(decoded_template, {"page": "one", "abc": "4"})

    def test_remove_param(self):
        context = get_context({"page": "one", "abc": "113"})
        template_to_render = Template(
            "{% load query_url %}" "{% param_replace abc=None %}"
        )
        rendered_template = template_to_render.render(context)
        rendered_template = unescape(rendered_template)
        decoded_template = dict(parse_qsl(rendered_template))
        self.assertDictEqual(decoded_template, {"page": "one"})

    def test_false_keeps_param(self):
        context = get_context({"page": "None", "abc": "113"})
        template_to_render = Template(
            "{% load query_url %}" "{% param_replace abc=False %}"
        )
        rendered_template = template_to_render.render(context)
        rendered_template = unescape(rendered_template)
        decoded_template = dict(parse_qsl(rendered_template))
        self.assertDictEqual(decoded_template, {"page": "None", "abc": "False"})
