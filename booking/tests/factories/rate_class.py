import factory

from booking.models import RateClass


class RateClassFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = RateClass

    class Params:
        name_base = factory.Faker("company")

    name = factory.LazyAttributeSequence(lambda o, n: f"{o.name_base} {n}")
    description = factory.Faker("paragraph")
    rate = factory.Faker("pydecimal", positive=True, right_digits=2, max_value=10 ** 4)
