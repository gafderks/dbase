from django.test import TestCase, override_settings

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

    @override_settings(SHOP_SKU_OFFSET=2365)
    def test_get_sku(self):
        material = MaterialFactory()
        self.assertEqual(
            material.sku,
            material.id + 2365,
        )

    @override_settings(SHOP_PRODUCT_URL_FORMAT="https://example.com/?p={sku}")
    def test_get_shop_url(self):
        material_lendable = MaterialFactory(lendable=True)
        self.assertEqual(
            material_lendable.get_shop_url(),
            f"https://example.com/?p={material_lendable.sku}",
        )
        material_non_lendable = MaterialFactory(lendable=False)
        self.assertEqual(material_non_lendable.get_shop_url(), None)

    @override_settings(SHOP_PRODUCT_URL_FORMAT="")
    def test_get_shop_url_no_setting(self):
        material_lendable = MaterialFactory(lendable=True)
        self.assertEqual(material_lendable.get_shop_url(), None)
        material_non_lendable = MaterialFactory(lendable=False)
        self.assertEqual(material_non_lendable.get_shop_url(), None)

    def test_lendable_stock(self):
        m1 = MaterialFactory(stock_value=5, lendable_stock_value=3, stock_unit="meter")
        self.assertEqual(m1.stock, "5 meter")
        self.assertEqual(m1.lendable_stock, "3 meter")
        m2 = MaterialFactory(stock_value=5, lendable_stock_value=3, stock_unit="")
        self.assertEqual(m2.stock, "5")
        self.assertEqual(m2.lendable_stock, "3")
        m3 = MaterialFactory(stock_value=5, lendable_stock_value=None, stock_unit="")
        self.assertEqual(m3.stock, "5")
        self.assertEqual(m3.lendable_stock, "5")
        m3 = MaterialFactory(
            stock_value=5, lendable_stock_value=None, stock_unit="inch"
        )
        self.assertEqual(m3.stock, "5 inch")
        self.assertEqual(m3.lendable_stock, "5 inch")
        m4 = MaterialFactory(
            stock_value=None, lendable_stock_value=None, stock_unit="pieces"
        )
        self.assertEqual(m4.stock, "")
        self.assertEqual(m4.lendable_stock, "")
        m5 = MaterialFactory(
            stock_value=None, lendable_stock_value=2, stock_unit="pieces"
        )
        self.assertEqual(m5.stock, "")
        self.assertEqual(m5.lendable_stock, "2 pieces")
        m6 = MaterialFactory(
            stock_value=23.88, lendable_stock_value=None, stock_unit=""
        )
        self.assertEqual(m6.stock, "23.88")
        m7 = MaterialFactory(stock_value=0.90, lendable_stock_value=None, stock_unit="")
        self.assertEqual(m7.stock, "0.9")
        m8 = MaterialFactory(stock_value=2.0, lendable_stock_value=None, stock_unit="")
        self.assertEqual(m8.stock, "2")
        m9 = MaterialFactory(
            stock_value=2.0001, lendable_stock_value=None, stock_unit=""
        )
        self.assertEqual(m9.stock, "2")
