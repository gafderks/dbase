import factory

from booking.models import Booking
from booking.tests.factories import GameFactory, MaterialFactory
from users.tests.factories import UserFactory


class BookingFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Booking

    requester = factory.SubFactory(UserFactory)
    game = factory.SubFactory(GameFactory, creator=factory.SelfAttribute("..requester"))
    material = factory.SubFactory(MaterialFactory)
    custom_material = None
    workweek = factory.Faker("pybool")
    comment = factory.Faker("paragraph")
    amount = factory.Faker("phone_number")
