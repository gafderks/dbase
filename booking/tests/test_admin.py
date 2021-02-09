from django.contrib.admin import AdminSite
from django.test import TestCase
from django.urls import reverse

from booking.admin import RateClassAdmin
from booking.forms import RateClassForm
from booking.models import RateClass, Material
from booking.tests.factories import RateClassFactory, MaterialFactory
from tests.utils import english
from users.tests.factories import SuperUserFactory


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


def get_form_data_for_rate_class(rate_class):
    return {
        "name": rate_class.name,
        "rate_0": rate_class.rate.amount,
        "rate_1": rate_class.rate.currency,
    }


class RateClassAdminTest(TestCase):
    def setUp(self):
        self.site = AdminSite()

    def test_add_material(self):
        rate_class_admin = RateClassAdmin(RateClass, self.site)
        # Create a rate class and material
        rate_class = RateClassFactory()
        mat = MaterialFactory(rate_class=None)
        # Add the material to the rate class through the form
        my_form = RateClassForm(
            {
                **get_form_data_for_rate_class(rate_class),
                "materials": [mat.pk],
            },
            instance=rate_class,
        )
        self.assertTrue(my_form.is_valid(), my_form.errors.as_data())
        # Save the model from the form
        rate_class_admin.save_model(
            obj=rate_class, form=my_form, change=None, request=None
        )
        mat.refresh_from_db()
        self.assertEqual(mat.rate_class, rate_class)

    def test_reassign_material(self):
        rate_class_admin = RateClassAdmin(RateClass, self.site)
        # Create a rate class and material
        rate_class = RateClassFactory()
        mat = MaterialFactory()
        old_rate_class = mat.rate_class
        # Add the material to the rate class through the form
        my_form = RateClassForm(
            {
                **get_form_data_for_rate_class(rate_class),
                "materials": [mat.pk],
            },
            instance=rate_class,
        )
        self.assertTrue(my_form.is_valid(), my_form.errors.as_data())
        # Save the model from the form
        rate_class_admin.save_model(
            obj=rate_class, form=my_form, change=None, request=None
        )
        mat.refresh_from_db()
        self.assertEqual(mat.rate_class, rate_class)
        self.assertTrue(mat in rate_class.materials.all())
        old_rate_class.refresh_from_db()
        self.assertFalse(mat in old_rate_class.materials.all())

    # TODO Test remove material
