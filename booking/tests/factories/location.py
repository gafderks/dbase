import factory

from booking.models import Location


class LocationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Location

    class Params:
        name_base = factory.Faker("company")

    name = factory.LazyAttributeSequence(lambda o, n: f"{o.name_base} {n}")
