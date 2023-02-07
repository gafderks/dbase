from django.test import TestCase
from django.urls import reverse
from tests.utils import english

from booking.forms import MaterialForm
from booking.tests.factories import MaterialFactory, MaterialAliasFactory
from users.tests.factories import SuperUserFactory


class MaterialFormTest(TestCase):
    def test_stock_value_placeholder(self):
        material = MaterialFactory.create(stock_value=30.0000)
        self.client.force_login(SuperUserFactory())
        response = self.client.get(
            reverse("admin:booking_material_change", args=(material.id,))
        )
        self.assertContains(response, f'value="30"')  # for stock_value
        self.assertContains(response, f'placeholder="30"')  # for lendable_stock_value

    @english
    def test_cannot_create_material_with_alias_name(self):
        MaterialAliasFactory.create(name="Inflatable")
        material = MaterialFactory.build()
        form = MaterialForm(data={"name": "Inflatable"}, instance=material)
        self.assertEquals(
            form.errors["name"],
            ["There exists already a material alias with the given name."],
        )
