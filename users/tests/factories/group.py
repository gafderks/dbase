import factory
from django.utils.text import slugify
from users.models import Group


class GroupFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Group

    name = factory.Sequence(lambda n: factory.Faker("company").generate() + f" {n}")
    slug = factory.LazyAttribute(lambda o: slugify(o.name))
    type = factory.Iterator([Group.GroupType.GROUP, Group.GroupType.COMMISSION])
