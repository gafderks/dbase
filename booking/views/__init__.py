from users.models import Group
from .event_view import EventView
from .event_game_view import EventGameView
from .event_list_view import EventListView
from .home_view import HomeView

from ..models import Event, PartOfDay, Material


# TODO much of the base context is needed for the navigation,
#  can we retrieve it there? Use Mixin?
def _get_base_context(request):
    return {
        "events": Event.objects.viewable(request.user),
        "groups": Group.objects.filter(type=Group.GroupType.GROUP),
        "commissions": Group.objects.filter(type=Group.GroupType.COMMISSION),
        "parts_of_day": PartOfDay.PART_OF_DAY_CHOICES,
        "typeahead_thumbprint": Material.last_modification().isoformat()
        if Material.last_modification() is not None
        else "never",
    }
