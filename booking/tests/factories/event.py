from datetime import timedelta

import factory
from datetime import timezone
from django.utils.text import slugify

from booking.models import Event


class EventFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Event

    class Params:
        name_base = factory.Faker("company")

    name = factory.LazyAttributeSequence(lambda o, n: f"{o.name_base} {n}")
    slug = factory.LazyAttribute(lambda o: slugify(o.name))
    booking_start = factory.Faker("past_datetime", tzinfo=timezone.utc)
    privileged_booking_end = factory.Faker("future_datetime", tzinfo=timezone.utc)
    booking_end = factory.LazyAttribute(
        lambda o: o.privileged_booking_end + timedelta(days=3)
    )
    event_start = factory.LazyAttribute(
        lambda o: o.privileged_booking_end + timedelta(days=24)
    )
    event_end = factory.LazyAttribute(lambda o: o.event_start + timedelta(days=5))
    visible = True
