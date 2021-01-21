from django.test import TestCase

from booking.models import Material, Category
from booking.tests.factories import MaterialFactory, CategoryFactory


class CategoryModelTest(TestCase):
    def test_delete_category_keeps_materials(self):
        category = CategoryFactory()
        material = MaterialFactory()
        material.categories.add(category)
        category.delete()
        self.assertEqual(Material.objects.count(), 1)
        self.assertEqual(Category.objects.count(), 0)

    def test_category_tree(self):
        base = CategoryFactory()
        child = CategoryFactory(parent=base)
        grandchild = CategoryFactory(parent=child)
        self.assertTrue(base in grandchild.get_ancestors())
