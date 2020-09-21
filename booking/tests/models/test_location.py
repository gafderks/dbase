from django.test import TestCase

from booking.models import Location, Material
from booking.tests.factories import MaterialFactory, LocationFactory


class LocationModelTest(TestCase):
    def test_delete_location_keeps_materials(self):
        location = LocationFactory()
        material = MaterialFactory(location=location)
        location.delete()
        self.assertEqual(Material.objects.count(), 1)
        self.assertEqual(Location.objects.count(), 0)
