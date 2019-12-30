from django.urls import path

from . import forms
import django.contrib.auth.views as auth_views

app_name = "users"
urlpatterns = [
    path(
        "login/",
        auth_views.LoginView.as_view(authentication_form=forms.UserLoginForm),
        name="login",
    ),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
]
