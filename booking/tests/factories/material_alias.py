import factory

from booking.models import MaterialAlias
from booking.tests.factories import MaterialFactory


class MaterialAliasFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = MaterialAlias

    name = factory.Faker("company")
    material = factory.SubFactory(MaterialFactory)
