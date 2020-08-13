import factory
from django.utils import timezone
from django.utils.text import slugify
from datetime import timedelta
from booking.models import Event


class EventFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Event

    name = factory.Faker("company")
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
