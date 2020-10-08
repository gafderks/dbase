from django.shortcuts import redirect

from booking.forms import GameForm
from booking.models import Game, PartOfDay
from booking.views import EventView


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
