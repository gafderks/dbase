from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Field
from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from booking.models import Material, Category


class UserLoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super(UserLoginForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Field('username', template='crispy/floating-labels.html'),
            Field('password', template='crispy/floating-labels.html'),
            Submit('submit', _('Login'), css_class='btn btn-lg btn-primary btn-block')
        )


class MaterialForm(forms.ModelForm):
    class Meta:
        model = Material
        fields = '__all__'
        help_texts = {

        }
        error_messages = {

        }

    def __init__(self, *args, **kwargs):
        super(MaterialForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', _('Submit')))


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = '__all__'
        help_texts = {

        }
        error_messages = {

        }

    def __init__(self, *args, **kwargs):
        super(CategoryForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', _('Submit')))
