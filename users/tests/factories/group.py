import factory
from django.utils.text import slugify
from users.models import Group


class GroupFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Group

    class Params:
        name_base = factory.Faker("company")

    name = factory.LazyAttributeSequence(lambda o, n: f"{o.name_base} {n}")
    slug = factory.LazyAttribute(lambda o: slugify(o.name))
    type = factory.Iterator([Group.GroupType.GROUP, Group.GroupType.COMMISSION])
