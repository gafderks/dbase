import factory

from booking.models import MaterialImage
from booking.tests.factories import MaterialFactory


class MaterialImageFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = MaterialImage

    material = factory.SubFactory(MaterialFactory)
    image = factory.django.ImageField()
