from django import forms
from django.utils.translation import gettext_lazy as _
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

from booking.models import Material, Category, Event


class MaterialForm(forms.ModelForm):
    class Meta:
        model = Material
        fields = "__all__"
        help_texts = {}
        error_messages = {}

    def __init__(self, *args, **kwargs):
        super(MaterialForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.add_input(Submit("submit", _("Submit")))


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = "__all__"
        help_texts = {}
        error_messages = {}

    def __init__(self, *args, **kwargs):
        super(CategoryForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.add_input(Submit("submit", _("Submit")))


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = "__all__"

    def clean(self):
        cleaned_data = super().clean()
        print(cleaned_data)
        booking_start = cleaned_data.get("booking_start")
        booking_end = cleaned_data.get("booking_end")
        privileged_booking_end = cleaned_data.get("privileged_booking_end")
        event_start = cleaned_data.get("event_start")
        event_end = cleaned_data.get("event_end")

        if booking_end and booking_start and booking_end < booking_start:
            raise forms.ValidationError(
                _("Booking end cannot be earlier than booking start.")
            )
        if (
            privileged_booking_end
            and booking_end
            and privileged_booking_end < booking_end
        ):
            raise forms.ValidationError(
                _("Privileged booking end cannot be earlier than booking end.")
            )
        if event_end and event_start and event_end < event_start:
            raise forms.ValidationError(
                _("Event end cannot be earlier than event start.")
            )
        return cleaned_data
