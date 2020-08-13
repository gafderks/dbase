import factory
from users.models import User
from users.tests.factories import GroupFactory


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    password = factory.Faker("password")
    email = factory.Faker("safe_email")
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    group = factory.SubFactory(GroupFactory)
