from django.test import TestCase
from django.urls import reverse
from tests.utils import english

from booking.forms import MaterialForm
from django.forms.models import model_to_dict
from booking.tests.factories import (
    MaterialFactory,
    MaterialAliasFactory,
    CategoryFactory,
)
from users.tests.factories import SuperUserFactory


class MaterialFormTest(TestCase):
    def test_can_add_material(self):
        category = CategoryFactory.create()
        material = MaterialFactory.create(categories=[category])
        form = MaterialForm(
            data={
                **model_to_dict(material),
                "name": "Unique name",
            }
        )
        self.assertTrue(form.is_valid())

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
        form = MaterialForm(data={"name": "Inflatable"})
        self.assertFalse(form.is_valid())
        self.assertEquals(
            form.errors["name"],
            ["There exists already a material alias with the given name."],
        )

    @english
    def test_non_negative_stock_value(self):
        form = MaterialForm(data={"stock_value": -4})
        self.assertEquals(
            form.errors["stock_value"], ["Stock value must not be negative."]
        )

    @english
    def test_non_negative_lendable_stock_value(self):
        form = MaterialForm(data={"lendable_stock_value": -4})
        self.assertEquals(
            form.errors["lendable_stock_value"],
            ["Lendable stock value must not be negative."],
        )

    @english
    def test_lendable_stock_not_smaller_than_stock(self):
        form = MaterialForm(data={"stock_value": 2, "lendable_stock_value": 3})
        self.assertEquals(
            form.errors["lendable_stock_value"],
            ["Lendable stock value must not be more than stock value."],
        )

    @english
    def test_disable_lendable_if_lendable_stock_is_set_to_zero(self):
        material = MaterialFactory.create(lendable=True, categories=[CategoryFactory()])
        form = MaterialForm(
            data={**model_to_dict(material), "lendable_stock_value": 0},
            instance=material,
        )
        form.save()
        self.assertFalse(material.lendable)

    @english
    def test_enable_lendable_if_lendable_stock_is_set(self):
        material = MaterialFactory.create(
            lendable=False,
            lendable_stock_value=None,
            stock_value=2,
            categories=[CategoryFactory()],
        )
        form = MaterialForm(
            data={**model_to_dict(material), "lendable_stock_value": 1},
            instance=material,
        )
        form.save()
        self.assertTrue(material.lendable)
