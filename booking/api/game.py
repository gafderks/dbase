import uuid

from crispy_forms.utils import render_crispy_form
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseBadRequest, JsonResponse
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string

from booking.forms import GameForm, BookingForm
from booking.models import Game, PartOfDay


def _get_game_order(game):
    return [
        [the_game.pk, the_game.order]
        for the_game in Game.objects.filter(
            event=game.event, group=game.group, day=game.day
        )
    ]


def _get_nav_html(game, request):
    return render_to_string(
        "booking/partials/day-nav.html",
        {
            "games": {
                part_of_day: Game.objects.filter(
                    event=game.event,
                    group=game.group,
                    day=game.day,
                    part_of_day=part_of_day,
                )
                for part_of_day, _ in PartOfDay.PART_OF_DAY_CHOICES
            },
            "day": game.day,
            "parts_of_day": PartOfDay.PART_OF_DAY_CHOICES,
        },
        request=request,
    )


def _get_game_response(game, request):
    form_html = render_crispy_form(
        GameForm(instance=game, auto_id="id_%s_" + uuid.uuid4().hex)
    )
    game_html = render_to_string(
        "booking/partials/game-card.html",
        {
            "game": game,
            "gameform": GameForm(instance=game, auto_id="id_%s_" + uuid.uuid4().hex),
            "bookingform": BookingForm(
                initial={"game": game}, auto_id="id_%s_" + uuid.uuid4().hex
            ),
        },
        request=request,
    )
    return {
        "form_html": form_html,
        "game_html": game_html,
        "nav_html": _get_nav_html(game, request),
        "order": _get_game_order(game),
    }


@login_required
def move_game(request, game_id, direction):
    game = get_object_or_404(Game, pk=game_id)

    if direction not in ["up", "down", None]:
        return HttpResponseBadRequest("Unknown direction")

    if not game.user_may_edit(request.user):
        raise PermissionDenied("User may not edit game")

    if direction == "up":
        game.up()
    elif direction == "down":
        game.down()

    return JsonResponse({"success": True, **_get_game_response(game, request)})


@login_required
def delete_game(request, game_id):
    game = get_object_or_404(Game, pk=game_id)

    if not game.user_may_edit(request.user):
        raise PermissionDenied("User may not delete game")

    game.delete()

    return JsonResponse(
        {
            "success": True,
            "order": _get_game_order(game),
            "nav_html": _get_nav_html(game, request),
        }
    )


@login_required
def edit_game(request, game_id=None):
    """
    View for adding a new game to the database.

    :param game_id:
    :param request:
    :return:
    """
    if game_id:
        game = get_object_or_404(Game, pk=game_id)
    else:
        game = Game(creator=request.user)

    form = GameForm(request.POST or None, instance=game)
    if request.POST and form.is_valid():
        # check the permissions
        if not game.user_may_edit(request.user):
            raise PermissionDenied("User may not edit game")

        game = form.save()
        return JsonResponse({"success": True, **_get_game_response(game, request)})

    form_html = render_crispy_form(form)
    return JsonResponse({"success": False, "form_html": form_html})
