import factory

from booking.models import Material


class MaterialFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Material

    name = factory.Sequence(
        lambda n: factory.Faker("company").generate({"locale": None}) + f" {n}"
    )
    description = factory.Faker("paragraph")

    gm = factory.Faker("pybool")
    location = factory.SubFactory("booking.tests.factories.LocationFactory")

    @factory.post_generation
    def categories(self, create, extracted, **kwargs):
        if not create:
            # Simple build, do nothing.
            return

        if extracted:
            # A list of groups were passed in, use them
            for category in extracted:
                self.categories.add(category)

    rate_class = factory.SubFactory("booking.tests.factories.RateClassFactory")
    images = factory.RelatedFactoryList(
        "booking.tests.factories.MaterialImageFactory", factory_related_name="material"
    )
    attachments = factory.RelatedFactoryList(
        "booking.tests.factories.MaterialAttachmentFactory",
        factory_related_name="material",
    )
    aliases = factory.RelatedFactoryList(
        "booking.tests.factories.MaterialAliasFactory", factory_related_name="material"
    )
