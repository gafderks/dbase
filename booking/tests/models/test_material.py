from django.test import TestCase

from booking.models import (
    MaterialAlias,
    Material,
    MaterialAttachment,
    MaterialImage,
    Booking,
)
from booking.tests.factories import (
    MaterialFactory,
    MaterialAttachmentFactory,
    MaterialAliasFactory,
    MaterialImageFactory,
    BookingFactory,
)


class MaterialModelTest(TestCase):
    def test_can_delete_material_with_material_alias(self):
        material = MaterialFactory()
        material_alias = MaterialAliasFactory(material=material)
        material.delete()
        self.assertEqual(Material.objects.count(), 0)
        self.assertEqual(MaterialAlias.objects.count(), 0)

    def test_can_delete_material_with_material_attachment(self):
        material = MaterialFactory()
        material_attachment = MaterialAttachmentFactory(material=material)
        material.delete()
        self.assertEqual(Material.objects.count(), 0)
        self.assertEqual(MaterialAttachment.objects.count(), 0)

    def test_can_delete_material_with_material_image(self):
        material = MaterialFactory()
        material_image = MaterialImageFactory(material=material)
        material.delete()
        self.assertEqual(Material.objects.count(), 0)
        self.assertEqual(MaterialImage.objects.count(), 0)

    def test_delete_material_with_bookings(self):
        material = MaterialFactory()
        material_name = material.name
        booking = BookingFactory(material=material)
        material.delete()
        booking.refresh_from_db()
        self.assertEqual(Material.objects.count(), 0, "material was not deleted")
        self.assertEqual(Booking.objects.count(), 1, "booking was deleted")
        self.assertEqual(booking.material, None, "booking still refers to material")
        self.assertEqual(
            booking.custom_material,
            material_name,
            "booking does not have material name",
        )
