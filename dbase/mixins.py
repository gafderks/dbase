from django.shortcuts import render
from django.views.generic.base import ContextMixin

from dbase.user_alert_exception import UserAlertException
from users.group_permission_error import GroupPermissionError


class UserAlertMixin(ContextMixin):
    """Catches user alerts and displays them to the user."""

    def dispatch(self, request, *args, **kwargs):
        try:
            return super().dispatch(request, *args, **kwargs)
        except UserAlertException as e:
            return render(request, "theme/alert.html", {"message": str(e)})
        except GroupPermissionError as e:
            return render(
                request,
                "theme/alert.html",
                {"message": str(e)},
                status=403,  # Forbidden
            )
