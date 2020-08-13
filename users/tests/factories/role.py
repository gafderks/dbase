import factory
from users.models import Role


class RoleFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Role
