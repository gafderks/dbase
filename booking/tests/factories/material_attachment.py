import factory

from booking.models import MaterialAttachment
from booking.tests.factories import MaterialFactory


class MaterialAttachmentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = MaterialAttachment

    attachment = factory.django.FileField()
    material = factory.SubFactory(MaterialFactory)
    description = factory.Faker("paragraph")
