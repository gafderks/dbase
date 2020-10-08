from booking.filters import BookingFilter
from booking.models import Booking, PartOfDay
from booking.models.list_view_filter import ListView
from booking.views import EventView


class EventListView(EventView):
    template_name = "booking/event/list-view.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get the bookings for this event and group, also apply filter from UI
        current_event = context["current_event"]
        bookings = BookingFilter(
            self.request.GET,
            request=self.request,
            queryset=Booking.objects.prefetch_related(
                "material",
                "material__categories",
                "game",
                "game__group",
            ).filter(
                game__event=current_event,
                **self.get_group_filter(context["current_group"], "game__")
            ),
        )

        # Arrange the bookings in lists using the ListViewFilters per day and part of
        #  day
        list_views = {
            day: {
                part_of_day: ListView().get_lists(
                    bookings.qs.filter(
                        game__day=day,
                        game__part_of_day=part_of_day,
                    ),
                )
                for part_of_day, _ in PartOfDay.PART_OF_DAY_CHOICES
            }
            for day in current_event.days
        }

        context.update({"list_views": list_views, "filter": bookings})

        return context
