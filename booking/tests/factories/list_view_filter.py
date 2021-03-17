import factory

from booking.models import ListViewFilter


class ListViewFilterFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ListViewFilter

    class Params:
        name_base = factory.Faker("company")

    name = factory.LazyAttributeSequence(lambda o, n: f"{o.name_base} {n}")
    description = factory.Faker("paragraph")
    enabled = True

    @factory.post_generation
    def included_categories(self, create, extracted, **kwargs):
        if not create:
            # Simple build, do nothing.
            return

        if extracted:
            # A list of groups were passed in, use them
            for category in extracted:
                self.included_categories.add(category)

    @factory.post_generation
    def excluded_categories(self, create, extracted, **kwargs):
        if not create:
            # Simple build, do nothing.
            return

        if extracted:
            # A list of groups were passed in, use them
            for category in extracted:
                self.excluded_categories.add(category)

    gm = None
