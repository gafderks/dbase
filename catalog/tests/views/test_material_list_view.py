from unittest.mock import Mock

from django.conf import settings
from django.test import TestCase
from django.urls import reverse

from booking.tests.factories import MaterialFactory, CategoryFactory
from catalog.views.material_list_view import get_pages
from users.tests.factories import UserFactory


def get_page_context(page_no, num_pages):
    page_obj = Mock(number=page_no)
    paginator = Mock(num_pages=num_pages)
    return {"page_obj": page_obj, "paginator": paginator}


class MaterialListViewTest(TestCase):
    def test_get_pages(self):
        self.assertEqual(
            get_pages(get_page_context(10, 30), max_pages=8),
            range(10 - 4, 10 + 4 + 1),
        )
        self.assertEqual(
            get_pages(get_page_context(10, 30), max_pages=9),
            range(10 - 4, 10 + 4 + 1),
            "no integer division on odd max_pages",
        )
        self.assertEqual(
            get_pages(get_page_context(1, 30), max_pages=8),
            range(1, 1 + 8 + 1),
            "right margin not filled",
        )
        self.assertEqual(
            get_pages(get_page_context(27, 30), max_pages=8),
            range(27 - 4 - 1, 30 + 1),
            "left margin not filled",
        )
        self.assertEqual(
            get_pages(get_page_context(12, 30), max_pages=0),
            range(12, 12 + 1),
        )
        self.assertEqual(
            get_pages(get_page_context(12, 30), max_pages=40),
            range(1, 30 + 1),
        )

    def test_redirects_to_login(self):
        url = reverse("catalog:catalog")
        response = self.client.get(url)
        self.assertRedirects(
            response,
            reverse(settings.LOGIN_URL) + "?next=" + url,
        )

    def test_no_materials(self):
        self.client.force_login(UserFactory())
        response = self.client.get(reverse("catalog:catalog"))
        self.assertTemplateUsed(response, "catalog/material_list.html")

    def test_materials_listed(self):
        materials = MaterialFactory.create_batch(5)
        self.client.force_login(UserFactory())
        response = self.client.get(reverse("catalog:catalog"))
        self.assertTemplateUsed(response, "catalog/material_list.html")
        for material in materials:
            self.assertContains(response, str(material))

    def test_materials_filter_category(self):
        category = CategoryFactory()
        other_category = CategoryFactory()
        materials_in_category = MaterialFactory.create_batch(5, categories=[category])
        materials_other_category = MaterialFactory.create_batch(
            5, categories=[other_category]
        )
        self.client.force_login(UserFactory())
        response = self.client.get(category.get_absolute_url())
        self.assertTemplateUsed(response, "catalog/material_list.html")
        for material in materials_in_category:
            self.assertContains(response, str(material))
        for material in materials_other_category:
            self.assertNotContains(response, str(material))
        # Check that the category filter buttons are in the response
        self.assertContains(response, str(category))
        self.assertContains(response, str(other_category))
