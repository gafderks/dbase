from django.test import TestCase, RequestFactory
from django.views import View

from dbase.mixins import UserAlertMixin
from dbase.user_alert_exception import UserAlertException


class TestUserAlertMixin(TestCase):
    class DummyView(UserAlertMixin, View):
        def get(self, request, *args, **kwargs):
            raise UserAlertException("The message")

    def test_get_context_data_empty(self):
        request = RequestFactory().get("/non-existent")

        response = self.DummyView.as_view()(request=request)
        # Cannot use assertTemplate used due to not using Django test Client
        self.assertContains(
            response,
            '<div class="alert alert-info',
            msg_prefix="response did not use the correct template",
        )
        self.assertContains(
            response,
            "The message",
            msg_prefix="exception message is not part of response",
        )
