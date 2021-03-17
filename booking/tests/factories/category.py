import factory

from booking.models import Category


class CategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Category

    class Params:
        name_base = factory.Faker("company")

    name = factory.LazyAttributeSequence(lambda o, n: f"{o.name_base} {n}")
    description = factory.Faker("paragraph")
    parent = None
