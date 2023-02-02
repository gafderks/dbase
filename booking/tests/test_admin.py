from django.contrib.admin import AdminSite
from django.test import TestCase
from django.urls import reverse

from booking.admin import RateClassAdmin
from booking.forms import RateClassForm
from booking.models import RateClass
from booking.tests.factories import RateClassFactory, MaterialFactory, CategoryFactory
from tests.utils import english
from users.tests.factories import SuperUserFactory, UserFactory, RoleFactory


class MaterialAdminTest(TestCase):
    @english
    def test_camera_button(self):
        self.client.force_login(SuperUserFactory())
        response = self.client.get(reverse("admin:booking_material_changelist"))
        self.assertTemplateUsed(
            response, "camera/material_change_list_camera_button.html"
        )
        self.assertContains(response, "Camera")
        self.assertContains(response, reverse("camera:index"))


class RateClassAdminTest(TestCase):
    def setUp(self):
        self.site = AdminSite()

    def run_form(self, rate_class, materials):
        rate_class_admin = RateClassAdmin(RateClass, self.site)
        my_form = RateClassForm(
            {
                "name": rate_class.name,
                "rate_0": rate_class.rate.amount,
                "rate_1": rate_class.rate.currency,
                "materials": [material.pk for material in materials],
            },
            instance=rate_class,
        )
        self.assertTrue(my_form.is_valid(), my_form.errors.as_data())
        # Save the model from the form
        rate_class_admin.save_model(
            obj=rate_class, form=my_form, change=None, request=None
        )

    def test_edit_rate_class_add_material(self):
        rate_class = RateClassFactory()
        material = MaterialFactory(rate_class=None)
        # Add the material to the rate class through the form
        self.run_form(rate_class, [material])
        # Verify that the material is now associated to the rate class
        material.refresh_from_db()
        self.assertEqual(material.rate_class, rate_class)

    def test_edit_rate_class_reassign_material(self):
        # Create a rate class and material
        rate_class = RateClassFactory()
        material = MaterialFactory()
        old_rate_class = material.rate_class
        # Add the material to the rate class through the form
        self.run_form(rate_class, [material])
        material.refresh_from_db()
        # Verify that the rate class for the material was updated
        self.assertEqual(material.rate_class, rate_class)
        # Verify that the reverse relation holds as well
        self.assertTrue(material in rate_class.materials.all())
        # Verify that the material is no longer associated to the old rate class
        old_rate_class.refresh_from_db()
        self.assertFalse(material in old_rate_class.materials.all())

    def test_edit_rate_class_remove_material(self):
        rate_class = RateClassFactory()
        materials = MaterialFactory.create_batch(5, rate_class=rate_class)
        # Only keep the first 4 materials associated to the rate class
        self.run_form(rate_class, materials[:4])
        for material in materials:
            material.refresh_from_db()
        # Verify that the first 4 materials are still associated
        for material in materials[:4]:
            self.assertEqual(material.rate_class, rate_class)
        # Verify that the 5th is no longer associated
        self.assertEqual(materials[4].rate_class, None)

    def test_create_rate_class_without_materials(self):
        rate_class = RateClassFactory.build()  # do not save to DB
        self.assertFalse(RateClass.objects.all())  # verify that it is not in DB
        self.run_form(rate_class, [])
        # Verify that the rate class has been saved
        self.assertEqual(list(RateClass.objects.all()), [rate_class])

    def test_create_rate_class_with_materials(self):
        rate_class = RateClassFactory.build()  # do not save to DB
        self.assertFalse(RateClass.objects.all())  # verify that it is not in DB
        materials = MaterialFactory.create_batch(3, rate_class=None)
        self.run_form(rate_class, materials)
        # Verify that the rate class has been saved
        self.assertEqual(list(RateClass.objects.all()), [rate_class])
        for material in materials:
            material.refresh_from_db()
        # Verify that all materials were associated
        for material in materials:
            self.assertEqual(material.rate_class, rate_class)


class CategoryAdminTest(TestCase):
    def test_view_category(self):
        category = CategoryFactory()
        role = RoleFactory.create(permissions=["view_category", "view_admin"])
        user = UserFactory.create(groups=[role])
        self.client.force_login(user)
        response = self.client.get(reverse("admin:booking_category_changelist"))
        self.assertEqual(response.status_code, 200)
        response = self.client.get(reverse("admin:booking_category_tree_json"))
        self.assertContains(response, category.name)
