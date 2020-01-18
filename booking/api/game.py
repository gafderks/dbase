from crispy_forms.utils import render_crispy_form
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseBadRequest, JsonResponse
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string

from booking.forms import GameForm
from booking.models import Game


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

    form_html = render_crispy_form(GameForm(instance=game))
    game_html = render_to_string(
        "booking/partials/game-card.html",
        {"game": game, "form": GameForm(instance=game)},
    )
    order = [
        [the_game.pk, the_game.order]
        for the_game in Game.objects.filter(
            event=game.event, group=game.group, day=game.day
        )
    ]

    return JsonResponse(
        {
            "success": True,
            "form_html": form_html,
            "game_html": game_html,
            "order": order,
        }
    )


@login_required
def delete_game(request, game_id):
    game = get_object_or_404(Game, pk=game_id)

    if not game.user_may_edit(request.user):
        raise PermissionDenied("User may not delete game")

    game.delete()

    order = [
        [the_game.pk, the_game.order]
        for the_game in Game.objects.filter(
            event=game.event, group=game.group, day=game.day
        )
    ]

    return JsonResponse({"success": True, "order": order,})


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

        form_html = render_crispy_form(GameForm(instance=game))
        game_html = render_to_string(
            "booking/partials/game-card.html",
            {"game": game, "form": GameForm(instance=game)},
        )

        order = [
            [the_game.pk, the_game.order]
            for the_game in Game.objects.filter(
                event=game.event, day=game.day, group=game.group
            )
        ]

        return JsonResponse(
            {
                "success": True,
                "form_html": form_html,
                "game_html": game_html,
                "order": order,
            }
        )

    form_html = render_crispy_form(form)
    return JsonResponse({"success": False, "form_html": form_html})
