from django.urls import path

from . import views
from . import game

app_name = "api"
urlpatterns = [
    path("material", views.export_material, name="material"),
    path("materialalias", views.export_materialalias, name="materialalias"),
    path("game/new", game.edit_game, name="new_game"),
    path("game/edit/<int:game_id>", game.edit_game, name="edit_game"),
    path("game/delete/<int:game_id>", game.delete_game, name="delete_game"),
    path(
        "game/edit/<int:game_id>/move/<str:direction>",
        game.move_game,
        name="move_game",
    ),
]
