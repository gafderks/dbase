import factory

from booking.models import MaterialAlias
from booking.tests.factories import MaterialFactory


class MaterialAliasFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = MaterialAlias

    class Params:
        name_base = factory.Faker("company")

    name = factory.LazyAttributeSequence(lambda o, n: f"{o.name_base} {n}")
    material = factory.SubFactory(MaterialFactory)
