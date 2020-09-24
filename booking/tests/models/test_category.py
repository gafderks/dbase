from django.test import TestCase

from booking.models import Material, Category
from booking.tests.factories import MaterialFactory, CategoryFactory


class RateClassModelTest(TestCase):
    def test_delete_category_keeps_materials(self):
        category = CategoryFactory()
        material = MaterialFactory()
        material.categories.add(category)
        category.delete()
        self.assertEqual(Material.objects.count(), 1)
        self.assertEqual(Category.objects.count(), 0)
