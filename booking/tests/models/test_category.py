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

    def test_category_ancestors(self):
        base = CategoryFactory()
        child = CategoryFactory(parent=base)
        grandchild = CategoryFactory(parent=child)
        self.assertTrue(base in grandchild.get_ancestors())
        self.assertTrue(child in grandchild.get_ancestors())
        self.assertFalse(child in child.get_ancestors())
        self.assertFalse(grandchild in child.get_ancestors())

    def test_category_material_filter_parent(self):
        base = CategoryFactory()
        child = CategoryFactory(parent=base)
        grandchild = CategoryFactory(parent=child)
        material1 = MaterialFactory(categories=[child])
        self.assertTrue(
            material1
            in Material.objects.filter(
                categories__in=child.get_descendants(include_self=True)
            )
        )
        self.assertTrue(
            material1
            in Material.objects.filter(
                categories__in=base.get_descendants(include_self=True)
            )
        )
        self.assertFalse(
            material1
            in Material.objects.filter(
                categories__in=grandchild.get_descendants(include_self=True)
            )
        )
