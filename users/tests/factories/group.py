import factory
from django.utils.text import slugify
from users.models import Group


class GroupFactory(factory.DjangoModelFactory):
    class Meta:
        model = Group

    name = factory.Faker("company")
    slug = factory.LazyAttribute(lambda o: slugify(o.name))
    type = factory.Iterator([Group.GroupType.GROUP, Group.GroupType.COMMISSION])
