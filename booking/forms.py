from crispy_forms.bootstrap import InlineField
from django import forms
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.utils.translation import gettext as __
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Field, Div, Reset

from booking.models import Material, Category, Event, MaterialAlias, Game


class MaterialForm(forms.ModelForm):
    class Meta:
        model = Material
        fields = "__all__"

    def clean(self):
        cleaned_data = super().clean()

        name = cleaned_data.get("name")

        alias = MaterialAlias.objects.filter(name__iexact=name)
        if alias:
            raise forms.ValidationError(
                _("There exists already a material alias with the given name.")
            )
        return cleaned_data


class MaterialAliasForm(forms.ModelForm):
    class Meta:
        model = MaterialAlias
        fields = "__all__"

    def clean(self):
        cleaned_data = super().clean()

        name = cleaned_data.get("name")

        material = Material.objects.filter(name__iexact=name)
        if material:
            raise forms.ValidationError(
                _("There exists already a material with the given name.")
            )
        return cleaned_data


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


class GameForm(forms.ModelForm):
    class Meta:
        model = Game
        fields = "__all__"
        widgets = {
            "event": forms.HiddenInput(),
            "day": forms.HiddenInput(),
            "group": forms.HiddenInput(),
        }
        labels = {
            "name": __("Game name"),
            "location": "<i class='fas fa-map-marker-alt'></i> " + __("Location"),
            "part_of_day": "<i class='fas fa-clock'></i> " + __("Part of day"),
        }
        help_texts = {"name": None, "location": None, "part_of_day": None}

    def __init__(self, *args, **kwargs):
        super(GameForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        if self.instance.id:
            self.helper.form_action = reverse(
                "booking:api:edit_game", args=[self.instance.id]
            )
        else:
            self.helper.form_action = reverse("booking:api:new_game")
        self.helper.form_method = "POST"
        css_class = "game-form-update" if self.instance.id else "game-form-create"
        self.helper.form_class = "game-form " + css_class
        self.helper.layout = Layout(
            Div(
                Field(
                    "name",
                    template="crispy/floating-labels.html",
                    wrapper_class="col px-1 mb-lg-0",
                ),
                Field(
                    "part_of_day",
                    template="crispy/floating-labels.html",
                    wrapper_class="col-lg-3 px-1 mb-lg-0",
                ),
                Field(
                    "location",
                    template="crispy/floating-labels.html",
                    wrapper_class="col-lg-3 px-1 mb-lg-0",
                ),
                Div(
                    Submit(
                        "submit",
                        _("Update") if self.instance.id else _("Add"),
                        css_id=self.auto_id % "submit",
                    ),
                    css_class="col-auto px-1 mb-lg-0 form-label-group",
                ),
                Div(
                    Reset("reset", _("Cancel"), css_id=self.auto_id % "reset",),
                    css_class="col-auto px-1 mb-lg-0 form-label-group",
                )
                if self.instance.id
                else None,
                "event",
                "day",
                "group",
                css_class="row",
            ),
        )

    def clean(self):
        """
        Here we check whether the day of the game is part of the event.
        :return:
        """
        cleaned_data = super().clean()

        day = cleaned_data.get("day")
        event = cleaned_data.get("event")

        if day < event.event_start:
            raise forms.ValidationError(
                _("Day of game cannot be earlier than event start.")
            )

        if day > event.event_end:
            raise forms.ValidationError(
                _("Day of game cannot be later than event end.")
            )

        return cleaned_data
