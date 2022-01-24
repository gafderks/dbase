from django.urls import reverse
from selenium.webdriver.common.by import By

from functional_tests.base import FunctionalTest
from users.tests.factories import SuperUserFactory


class AdminTest(FunctionalTest):
    def test_camera_button(self):
        # Bob is a logged in superuser
        bob = SuperUserFactory(first_name="Bob")
        self.create_pre_authenticated_session(bob)

        # Bob opens the page for the material
        self.browser.get(
            self.live_server_url + reverse("admin:booking_material_changelist")
        )

        # Bob finds a button to the camera app that has an image of a camera
        self.wait_for(
            lambda: self.assertCSSElementExists(
                "svg.fa-camera", "camera icon not loaded"
            )
        )

        # Bob clicks the button
        self.browser.find_element(By.CSS_SELECTOR, "a[href='/camera/']").click()

        # Bob sees a video (with his face)
        self.wait_for(lambda: self.assertCSSElementExists("video"))

        # Bob also sees a shutter button
        self.assertCSSElementExists("button.camera-shutter")
