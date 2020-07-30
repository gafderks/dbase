import factory
from users.models import Role


class RoleFactory(factory.DjangoModelFactory):
    class Meta:
        model = Role
