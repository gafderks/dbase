from django.test import TestCase

from booking.models import Material, RateClass
from booking.tests.factories import MaterialFactory, RateClassFactory


class RateClassModelTest(TestCase):
    def test_delete_rateclass_keeps_materials(self):
        rateclass = RateClassFactory()
        material = MaterialFactory(rate_class=rateclass)
        rateclass.delete()
        self.assertEqual(Material.objects.count(), 1)
        self.assertEqual(RateClass.objects.count(), 0)
