from django.shortcuts import render
from django.views import View

from dbase.user_alert_exception import UserAlertException


class UserAlertMixin(View):
    """Catches user alerts and displays them to the user."""

    def dispatch(self, request, *args, **kwargs):
        try:
            return super().dispatch(request, *args, **kwargs)
        except UserAlertException as e:
            return render(request, "jeugdraad/alert.html", {"message": str(e)})
