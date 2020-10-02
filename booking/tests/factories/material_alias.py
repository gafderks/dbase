import factory

from booking.models import MaterialAlias
from booking.tests.factories import MaterialFactory


class MaterialAliasFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = MaterialAlias

    name = factory.Sequence(
        lambda n: factory.Faker("company").generate({"locale": None}) + f" {n}"
    )
    material = factory.SubFactory(MaterialFactory)
