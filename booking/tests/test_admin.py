from django.test import TestCase
from django.urls import reverse

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
