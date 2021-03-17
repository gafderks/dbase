import random

import factory
from factory import fuzzy

from booking.models import Game, PartOfDay
from booking.tests.factories import EventFactory
from users.tests.factories import UserFactory


class GameFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Game

    creator = factory.SubFactory(UserFactory)
    name = factory.Faker("company")
    event = factory.SubFactory(EventFactory)
    part_of_day = factory.fuzzy.FuzzyChoice(
        PartOfDay.PART_OF_DAY_CHOICES, getter=lambda c: c[0]
    )
    location = factory.Faker("sentence")
    group = factory.LazyAttribute(lambda g: g.creator.group)
    day = factory.Faker(
        "date_between_dates",
        date_start=factory.SelfAttribute("..event.event_start"),
        date_end=factory.SelfAttribute("..event.event_end"),
    )


class PopulatedGameFactory(GameFactory):
    bookings = factory.RelatedFactoryList(
        "booking.tests.factories.BookingFactory",
        factory_related_name="game",
        size=lambda: random.randint(1, 5),
    )
