from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import TemplateView

from booking.mixins import BookingPageMixin
from booking.models import Event
from dbase.user_alert_exception import UserAlertException
from users.group_permission_error import GroupPermissionError
from users.models import Group


class EventView(LoginRequiredMixin, BookingPageMixin, TemplateView):
    template_name = "booking/event/event.html"

    def get_requested_group(self, group_slug):
        """
        Translates a group slug in the request to a Group object or None if group_slug
        is "all". Also verifies whether the user doing the request may view the
        requested group.
        :param str group_slug: "all" | None | Group.slug
        :return Group: Group or None
        :raises UserAlertException: user is not assigned to a group and may not view
         bookings from other groups.
        """
        if group_slug == "all":
            requested_group = None
        elif group_slug is None:
            # No group was requested, so use user's own group, may be None
            requested_group = self.request.user.group
        else:
            requested_group = get_object_or_404(Group, slug=group_slug)

        # Check if user may view this group
        if not self.request.user.has_perm(
            "users.view_bookings_from_group", requested_group
        ):
            raise GroupPermissionError(
                _("You are not allowed to view bookings for this group.")
            )

        return requested_group

    def get_requested_event(self, event_slug):
        event = get_object_or_404(Event, slug=event_slug)
        if not self.request.user.has_perm("booking.view_event", event):
            raise UserAlertException(_("You are not allowed to view this event"))
        return event

    @staticmethod
    def get_group_filter(requested_group, filter_prefix=""):
        """
        Returns a filter dictionary for Games or Bookings that filters the requested
        group. If requested_group is None (all groups), an empty dict is returned, hence
        no filter.
        :param Group requested_group: Group | None
        :param str filter_prefix: prefix for the filter, e.g. game__, to filter groups
         of games of bookings.
        :return: dict
        """
        if requested_group is None:
            return dict()
        return {filter_prefix + "group": requested_group}

    def get_context_data(self, **kwargs):
        """Retrieves the requested event and the requested group"""
        context = super().get_context_data(**kwargs)
        context.update(
            {
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
        try:
            return super().get(request, *args, **kwargs)
        except GroupPermissionError as e:
            user_group = self.request.user.group
            if user_group is None:
                # Cannot use own group
                raise UserAlertException(
                    _(
                        "You are not assigned to a group. Please contact a board "
                        "member to resolve this issue."
                    )
                )
            else:
                return redirect(
                    reverse(
                        "booking:event_games_group",
                        kwargs={
                            "event_slug": self.kwargs.get("event_slug"),
                            "group_slug": user_group.slug,
                        },
                    )
                )
