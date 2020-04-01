from django.urls import path

from . import views
from . import game
from . import booking
from . import event

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
    path("booking/new", booking.edit_booking, name="new_booking"),
    path("booking/edit/<int:booking_id>", booking.edit_booking, name="edit_booking"),
    path(
        "booking/delete/<int:booking_id>", booking.delete_booking, name="delete_booking"
    ),
    path(
        "event/<slug:event_slug>/<slug:group_slug>/xlsx",
        event.EventExcelView.as_view(),
        name="excel_event",
    ),
]
