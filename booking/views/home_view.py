from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.utils.translation import gettext_lazy as _
from django.views.generic import View

from booking.models import Event
from dbase.mixins import UserAlertMixin
from dbase.user_alert_exception import UserAlertException


class HomeView(LoginRequiredMixin, UserAlertMixin, View):
    """
    Redirects user to the most recent open event or shows a message that there are no
    open events.
    """

    def get(self, request, *args, **kwargs):
        events = Event.objects.viewable(self.request.user)
        if not events:
            raise UserAlertException(_("There are no open events."))
        return redirect(events.first().get_absolute_url())
