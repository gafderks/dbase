import factory

from booking.models import RateClass


class RateClassFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = RateClass

    name = factory.Sequence(
        lambda n: factory.Faker("company").generate({"locale": None}) + f" {n}"
    )
    description = factory.Faker("paragraph")
    rate = factory.Faker("pydecimal", positive=True, right_digits=2, max_value=10 ** 4)
