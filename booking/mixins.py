from booking.models import Material, Event, PartOfDay
from dbase.mixins import UserAlertMixin
from users.models import Group


class NavigationMixin(UserAlertMixin):
    """Adds a base context that is needed for the navigation and controls"""

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        viewable_events = Event.objects.viewable(self.request.user)
        context.update(
            {
                "events": viewable_events,
                "current_event": viewable_events.first(),
                "typeahead_thumbprint": (
                    Material.last_modification().isoformat()
                    if Material.last_modification() is not None
                    else "never"
                ),
            }
        )
        return context


class BookingPageMixin(NavigationMixin):
    """Adds a base context that is needed for the booking controls"""

    extra_context = {
        "groups": Group.objects.filter(type=Group.GroupType.GROUP),
        "commissions": Group.objects.filter(type=Group.GroupType.COMMISSION),
        "parts_of_day": PartOfDay.PART_OF_DAY_CHOICES,
    }
