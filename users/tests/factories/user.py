import factory
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password

from users.tests.factories import GroupFactory


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = get_user_model()

    email = factory.Sequence(
        lambda n: str(n) + factory.Faker("safe_email").generate({"locale": None})
    )
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    group = factory.SubFactory(GroupFactory)

    # Role
    groups = factory.RelatedFactoryList(
        "users.tests.factories.RoleFactory", size=1, factory_related_name="user"
    )

    @factory.post_generation
    def password(self, create, extracted, **kwargs):
        if extracted is None:
            self.password = UserFactory.PASSWORD
        else:
            self.password = make_password(extracted)


UserFactory.PASSWORD = make_password("password")


class SuperUserFactory(UserFactory):
    is_superuser = True
