from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.utils.translation import gettext_lazy as _
from django.views.generic import View


class HomeView(LoginRequiredMixin, View):
    """
    Redirects user to the most recent open event or shows a message that there are no
    open events.
    """

    def get(self, request, *args, **kwargs):
        from booking.views import _get_base_context

        context = _get_base_context(request)
        events = context["events"]
        if not events:
            return render(
                request,
                "jeugdraad/alert.html",
                {**context, "message": _("There are no open events.")},
            )
        return redirect(events.first().get_absolute_url())
