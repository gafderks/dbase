from django.contrib.auth import get_user_model
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
from users.tests.factories import UserFactory


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

    def test_delete_user_with_bookings(self):
        # User 1 and 2 are from the same group
        # User 3 is from a different group
        user = UserFactory()
        booking = BookingFactory(requester=user)
        group = user.group
        user2 = UserFactory(group=group)
        booking2 = BookingFactory(requester=user2)
        user3 = UserFactory()
        booking3 = BookingFactory(requester=user3)
        self.assertEqual(
            group,
            booking.requester.group,
            "booking1 not associated with requester group",
        )
        self.assertEqual(
            group,
            booking2.requester.group,
            "booking2 not associated with requester group",
        )
        self.assertNotEqual(
            booking.requester,
            booking2.requester,
            "bookings are associated with same requester",
        )
        num_users_before_delete = get_user_model().objects.count()
        user.delete()
        booking.refresh_from_db()
        user2.delete()
        booking2.refresh_from_db()
        user3.delete()
        booking3.refresh_from_db()
        # User 1 and 2 should be replaced by the same sentinel user
        # User 3 should be replaced by another sentinel user
        # User count should be decreased by one as user 1 and 2 are 'merged'.
        self.assertEqual(
            get_user_model().objects.count(),
            num_users_before_delete - 1,
            "users were not replaced",
        )
        self.assertEqual(Booking.objects.count(), 3, "booking was deleted")
        self.assertEqual(group, booking.requester.group, "booking1 changed group")
        self.assertEqual(group, booking2.requester.group, "booking2 changed group")
        self.assertEqual(
            booking.requester.email,
            f"deleted_user@{group}",
            "requester was not replaced with sentinel user",
        )
        self.assertEqual(
            booking2.requester.email,
            f"deleted_user@{group}",
            "requester was not replaced with sentinel user",
        )
        self.assertEqual(
            booking.requester,
            booking2.requester,
            "different sentinel users were used for the same group",
        )
        self.assertNotEqual(
            booking.requester,
            booking3.requester,
            "same sentinel user was used for different groups",
        )
