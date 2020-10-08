from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, render
from django.utils.translation import gettext_lazy as _
from django.views.generic import TemplateView

from booking.models import Event
from booking.views.user_alert_exception import UserAlertException
from users.models import Group


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
        # TODO maybe do a redirection? Only if user_group.slug !== group_slug.
        #  Really should do this
        return user_group

    def get_requested_event(self, event_slug):
        event = get_object_or_404(Event, slug=event_slug)
        if not self.request.user.has_perm("booking.view_event", event):
            raise UserAlertException(_("You are not allowed to view this event"))
        return event

    @staticmethod
    def get_group_filter(requested_group, filter_prefix=""):
        # TODO Use Q expression?
        if requested_group is None:
            return dict()
        return {filter_prefix + "group": requested_group}

    def get_context_data(self, **kwargs):
        from booking.views import _get_base_context

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
                {"message": str(e)},
            )
