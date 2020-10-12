from django.conf import settings
from django.test import TestCase
from django.urls import reverse

from booking.tests.factories import MaterialFactory, CategoryFactory
from tests.utils import english
from users.tests.factories import UserFactory


class MaterialDetailViewTest(TestCase):
    def test_redirects_to_login(self):
        material = MaterialFactory()
        response = self.client.get(material.get_absolute_url())
        self.assertRedirects(
            response,
            reverse(settings.LOGIN_URL) + "?next=" + material.get_absolute_url(),
        )

    @english
    def test_details_on_page(self):
        material = MaterialFactory(categories=[CategoryFactory()])
        self.client.force_login(UserFactory())
        response = self.client.get(material.get_absolute_url())
        self.assertTemplateUsed(response, "catalog/material_detail.html")
        self.assertContains(response, material.name)
        if material.gm:
            self.assertContains(response, "GM")
        self.assertContains(response, material.stock)
        for category in material.categories.all():
            self.assertContains(response, category.name)
        self.assertContains(response, material.description)
        self.assertContains(response, material.location.name)
        for attachment in material.attachments.all():
            self.assertContains(response, attachment.attachment.url)
            self.assertContains(response, attachment.description)
        for alias in material.aliases.all():
            self.assertContains(response, alias.name)

    def test_shop_url(self):
        lendable_material = MaterialFactory(lendable=True)
        self.client.force_login(UserFactory())
        response = self.client.get(lendable_material.get_absolute_url())
        self.assertTemplateUsed(response, "catalog/material_detail.html")
        self.assertContains(response, lendable_material.get_shop_url())
