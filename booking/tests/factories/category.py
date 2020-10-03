import factory

from booking.models import Category


class CategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Category

    name = factory.Sequence(
        lambda n: factory.Faker("company").generate({"locale": None}) + f" {n}"
    )
    description = factory.Faker("paragraph")
