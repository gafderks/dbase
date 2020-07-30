import factory
from booking.models import Material


class MaterialFactory(factory.DjangoModelFactory):
    class Meta:
        model = Material

    name = factory.Sequence(lambda n: factory.Faker("company").generate() + f" {n}")
    description = factory.Faker("paragraph")

    gm = factory.Faker("pybool")

    @factory.post_generation
    def categories(self, create, extracted, **kwargs):
        if not create:
            # Simple build, do nothing.
            return

        if extracted:
            # A list of groups were passed in, use them
            for category in extracted:
                self.categories.add(category)
