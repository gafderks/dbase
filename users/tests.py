from django.test import TestCase


class LoginPageTest(TestCase):
    def test_redirect_to_login_page(self):
        requested_page = "/"
        response = self.client.get(requested_page)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["location"], "/users/login/?next=" + requested_page)

    def test_uses_login_template(self):
        response = self.client.get("/users/login/")
        self.assertTemplateUsed(response, "registration/login.html")
