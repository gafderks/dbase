from django.conf import settings
from django.test import TestCase
from django.urls import reverse

from booking.tests.factories import MaterialFactory, CategoryFactory
from users.tests.factories import UserFactory


class MaterialDetailViewModalTest(TestCase):
    # Note that the material_card.template is tested already in MaterialDetailViewTest
    def test_redirects_to_login(self):
        material = MaterialFactory()
        response = self.client.get(material.get_absolute_url())
        self.assertRedirects(
            response,
            reverse(settings.LOGIN_URL) + "?next=" + material.get_absolute_url(),
        )

    def test_uses_material_card(self):
        material = MaterialFactory(categories=[CategoryFactory()])
        self.client.force_login(UserFactory())
        response = self.client.get(
            reverse("catalog:material_modal", kwargs={"pk": material.pk})
        )
        self.assertTemplateUsed(response, "catalog/material_card.html")
        self.assertContains(
            response, material.name
        )  # Check whether template rendered correctly.
