from time import sleep

from booking.tests.factories import MaterialFactory
from tests.utils import english
from users.tests.factories import UserFactory
from .base import FunctionalTest


@english
class CatalogMaterialTest(FunctionalTest):
    def setUp(self):
        super().setUp()
        self.material = MaterialFactory(name="beschuiten (rol)")

    def test_can_view_material_details(self):
        # Bob is a logged in user
        bob = UserFactory(first_name="Bob")
        self.create_pre_authenticated_session(bob)

        # Bob opens the page for the material
        self.browser.get(self.live_server_url + self.material.get_absolute_url())

        # TODO finish test
