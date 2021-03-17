import factory
from django.contrib.auth.models import Permission

from users.models import Role


class RoleFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Role

    class Params:
        name_base = factory.Faker("company")

    name = factory.LazyAttributeSequence(lambda o, n: f"{o.name_base} {n}")

    @factory.post_generation
    def permissions(self, create, extracted, **kwargs):
        if not create:
            # Simple build, do nothing.
            return

        if extracted:
            # A list of permissions were passed in, use them
            for permission in extracted:
                if isinstance(permission, Permission):
                    pass
                elif isinstance(permission, str):
                    permission = Permission.objects.get(codename=permission)
                else:
                    raise ValueError(
                        "Unsupported permission type, use codename (str) or Permission"
                    )
                self.permissions.add(permission)
            # By default assign no permissions
