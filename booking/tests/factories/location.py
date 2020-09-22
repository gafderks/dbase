import factory

from booking.models import Location


class LocationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Location

    name = factory.Sequence(lambda n: factory.Faker("company").generate() + f" {n}")
