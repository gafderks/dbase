import factory

from booking.models import Category


class CategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Category

    name = factory.Faker("company")
    description = factory.Faker("paragraph")
