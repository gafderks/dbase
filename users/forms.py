from .models import User
from django.contrib.auth.forms import (
    AuthenticationForm,
    UserCreationForm,
    UserChangeForm,
)
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Field
from crispy_bootstrap5.bootstrap5 import FloatingField
from django.utils.translation import gettext_lazy as _


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("email", "group")


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = ("email", "group")


class UserLoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super(UserLoginForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            FloatingField(
                "username",
                css_class="form-control",
            ),
            FloatingField(
                "password",
                css_class="form-control",
            ),
            Submit("submit", _("Login"), css_class="btn btn-lg btn-primary btn-block"),
        )
