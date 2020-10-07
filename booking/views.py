from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, get_object_or_404, redirect
from django.utils.translation import gettext_lazy as _
from django.views.generic import TemplateView, View

from booking.filters import BookingFilter
from booking.forms import GameForm
from booking.models import (
    Event,
    Game,
    PartOfDay,
    Booking,
    Material,
)
from booking.models.list_view_filter import ListView
from users.models import Group


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


class UserAlertException(Exception):
    """
    Used for exceptions that are appropriate to propagate to the user.
    """

    pass


class HomeView(LoginRequiredMixin, View):
    """
    Redirects user to the most recent open event or shows a message that there are no
    open events.
    """

    def get(self, request, *args, **kwargs):
        context = _get_base_context(request)
        events = context["events"]
        if not events:
            return render(
                request,
                "jeugdraad/alert.html",
                {**context, "message": _("There are no open events.")},
            )
        return redirect(events.first().get_absolute_url())


class EventView(LoginRequiredMixin, TemplateView):
    template_name = "booking/event/event.html"

    def get_requested_group(self, group_slug):
        user_group = self.request.user.group

        if self.request.user.has_perm("booking.view_others_groups_bookings"):
            if group_slug == "all":
                # Show all groups
                return None
            elif group_slug is None:
                return user_group
            else:
                # Show other group
                return get_object_or_404(Group, slug=group_slug)
        else:
            if user_group is None:
                # If user has no group and may not view other groups, show error
                raise UserAlertException(
                    _(
                        "You are not assigned to a group. Please contact a board "
                        "member to resolve this issue."
                    )
                )
        # Default to the users own group
        # TODO maybe do a redirection?
        return user_group

    def get_requested_event(self, event_slug):
        event = get_object_or_404(Event, slug=event_slug)
        if not self.request.user.has_perm("booking.view_event", event):
            raise UserAlertException(_("You are not allowed to view this event"))
        return event

    @staticmethod
    def get_group_filter(requested_group, filter_prefix=""):
        if requested_group is None:
            return dict()
        return {filter_prefix + "group": requested_group}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                **_get_base_context(self.request),
                "current_event": self.get_requested_event(
                    self.kwargs.get("event_slug")
                ),
                "current_group": self.get_requested_group(
                    self.kwargs.get("group_slug", None)
                ),
            }
        )
        return context

    def get(self, request, *args, **kwargs):
        # TODO create mixin for displaying user alerts that is used for home page no
        #  open events as well.
        try:
            return super().get(request, *args, **kwargs)
        except UserAlertException as e:
            return render(
                request,
                "jeugdraad/alert.html",
                {"message": e},
            )


class EventGameView(EventView):
    template_name = "booking/event/game-view.html"

    def dispatch(self, request, *args, **kwargs):
        # Redirect to the list view if all groups are requested
        group_slug = kwargs.get("group_slug", None)
        if group_slug is None and request.user.group is None:
            # If the user is not in a group and did not supply a group, show all groups
            group_slug = "all"
        if group_slug == "all":
            # There is no game view for all groups
            return redirect("booking:event_list_group", kwargs.get("event_slug"), "all")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        current_event = context["current_event"]

        # Get the games per day and part of day
        games = {
            day: {
                part_of_day: Game.objects.filter(
                    event=current_event,
                    day=day,
                    part_of_day=part_of_day,
                    **self.get_group_filter(context["current_group"])
                )
                for part_of_day, _ in PartOfDay.PART_OF_DAY_CHOICES
            }
            for day in current_event.days
        }

        # TODO Are the game_forms really necessary?
        game_forms = {
            day: GameForm(
                initial={
                    "event": current_event,
                    "day": day,
                    **self.get_group_filter(context["current_group"]),
                },
                auto_id="id_game_%s_" + str(day.isoformat()),
            )
            for day in current_event.days
        }

        context.update(
            {
                "game_forms": game_forms,
                "games": games,
            }
        )

        return context


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
