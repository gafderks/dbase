from django.test import TestCase
from django.urls import reverse
from users.tests.factories import UserFactory, RoleFactory


class UserModelTest(TestCase):
    def admin_response(self, user):
        self.client.force_login(user)
        response = self.client.get(reverse("admin:index"))
        return response.status_code

    def test_cannot_open_admin_without_role(self):
        user = UserFactory()
        self.assertFalse(user.is_staff)
        self.assertEqual(self.admin_response(user), 302)

    def test_cannot_open_admin_without_view_admin_permission(self):
        role_without_view_admin = RoleFactory.create(permissions=[])
        user = UserFactory(groups=[role_without_view_admin])
        self.assertFalse(user.is_staff)
        self.assertEqual(self.admin_response(user), 302)

    def test_can_open_admin_with_view_admin_permission(self):
        role = RoleFactory.create(permissions=["view_admin"])
        user = UserFactory.create(groups=[role])
        self.assertTrue(user.is_staff)
        self.assertEqual(self.admin_response(user), 200)
