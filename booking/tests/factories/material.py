import factory

from booking.models import Material


class MaterialFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Material

    class Params:
        name_base = factory.Faker("company")
        lendable_base = factory.Faker("pyfloat", min_value=0)

    name = factory.LazyAttributeSequence(lambda o, n: f"{o.name_base} {n}")
    description = factory.Faker("paragraph")

    gm = factory.Faker("pybool")
    location = factory.SubFactory("booking.tests.factories.LocationFactory")
    stock_value = factory.Faker("pyfloat", min_value=0)
    lendable_stock_value = factory.LazyAttribute(
        lambda o: min(o.lendable_base, o.stock_value)
    )
    stock_unit = factory.Faker("word")

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
