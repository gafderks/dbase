from django.urls import path, include

from .views import EventGameView, EventListView, HomeView

app_name = "booking"
urlpatterns = [
    path("", HomeView.as_view(), name="index"),
    path("<slug:event_slug>", EventGameView.as_view(), name="event_display"),
    path("<slug:event_slug>/games", EventGameView.as_view(), name="event_games"),
    path(
        "<slug:event_slug>/games/<slug:group_slug>",
        EventGameView.as_view(),
        name="event_games_group",
    ),
    path("<slug:event_slug>/list", EventListView.as_view(), name="event_list"),
    path(
        "<slug:event_slug>/list/<slug:group_slug>",
        EventListView.as_view(),
        name="event_list_group",
    ),
    path("api/", include("booking.api.urls")),
]
