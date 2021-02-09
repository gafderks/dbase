from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Field, Div, Reset
from django import forms
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.urls import reverse
from django.utils.translation import gettext as __
from django.utils.translation import gettext_lazy as _
from mptt.forms import TreeNodeMultipleChoiceField

from booking.models import (
    Material,
    Category,
    Event,
    MaterialAlias,
    Game,
    Booking,
    RateClass,
)


class MaterialForm(forms.ModelForm):
    categories = TreeNodeMultipleChoiceField(queryset=Category.objects.all())

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
        _("Game name"), _("Location"), _("Part of day")  # For detection by makemessages
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
                        "update" if self.instance.id else "add",
                        _("Update") if self.instance.id else _("Add"),
                        css_id=self.auto_id % "submit",
                        css_class="btn-outline-primary crispy-outline",
                    ),
                    css_class="col-auto px-1 mb-lg-0 form-label-group",
                ),
                Div(
                    Reset(
                        "reset",
                        _("Cancel"),
                        css_id=self.auto_id % "reset",
                    ),
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


class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = "__all__"
        widgets = {
            "game": forms.HiddenInput(),
            "material": forms.TextInput(),
            "custom_material": forms.HiddenInput(),
        }
        labels = {
            "material": "",
            "amount": __("Amount"),
            "workweek": __("Workweek"),
            "comment": "<i class='far fa-comment'></i> " + __("Comment"),
        }
        _("Amount"), _("Workweek"), _("Comment")  # For detection by makemessages
        help_texts = {
            "material": None,
            "amount": None,
            "workweek": None,
            "comment": None,
        }

    def __init__(self, *args, **kwargs):
        super(BookingForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        if self.instance.id:
            self.helper.form_action = reverse(
                "booking:api:edit_booking", args=[self.instance.id]
            )
        else:
            self.helper.form_action = reverse("booking:api:new_booking")
        self.helper.form_method = "POST"
        css_class = "booking-form-update" if self.instance.id else "booking-form-create"
        self.helper.form_class = "booking-form w-100 " + css_class
        material_id = ""
        material_name = ""
        if self.instance.material:
            material_id = self.instance.material.id
            material_name = self.instance.material.name
        if self.instance.custom_material:
            material_id = self.instance.custom_material
            material_name = self.instance.custom_material
        self.helper.layout = Layout(
            Div(
                Field(
                    "material",
                    wrapper_class="col-8 col-xl-3 px-1 mb-xl-0",
                    css_class="typeahead-materials floating-label-size",
                    placeholder=__("Material") + "*",
                    autocomplete="off",
                    data_materialid=material_id,
                    data_materialname=material_name,
                    data_invalidmessage=__("Choose a material"),
                    data_allowcustom="true",
                    data_notfoundtext=__("Material not found..."),
                    data_addcustomtext=__('Click to request "<em>{}</em>" anyway.'),
                    title=__("Material"),
                ),
                Field(
                    "amount",
                    template="crispy/floating-labels.html",
                    wrapper_class="col-4 col-xl-2 px-1 mb-xl-0",
                    autocomplete="off",
                    title=__("Amount"),
                ),
                Field(
                    "workweek",
                    wrapper_class="col-auto px-1 mb-xl-0",
                    template="crispy/floating-labels.html",
                    data_toggle="toggle",
                    data_on=__("Workweek"),
                    data_off=__("No"),
                ),
                Field(
                    "comment",
                    template="crispy/floating-labels.html",
                    wrapper_class="col px-1 mb-xl-0",
                    title=__("Comment"),
                ),
                Div(
                    Submit(
                        "submit",
                        _("Update") if self.instance.id else _("Add"),
                        css_id=self.auto_id % "submit",
                        css_class="btn-outline-primary crispy-outline",
                    ),
                    css_class="col-auto px-1 mb-xl-0 form-label-group",
                ),
                Div(
                    Reset(
                        "reset",
                        _("Cancel"),
                        css_id=self.auto_id % "reset",
                    ),
                    css_class="col-auto px-1 mb-xl-0 form-label-group",
                )
                if self.instance.id
                else None,
                "game",
                "custom_material",
                css_class="row mx-0",
            ),
        )
        _("Material"), _("Choose a material"), _("Workweek"), _("No"), _(
            "Choose a material"
        ), _("Material not found..."), _('Click to request "<em>{}</em>" anyway.'),

    def clean(self):
        """
        Here we check whether a material was chosen or a custom material name was given.
        :return:
        """
        cleaned_data = super().clean()

        material = cleaned_data.get("material")
        custom_material = cleaned_data.get("custom_material")

        if material is None and custom_material is None:
            raise forms.ValidationError(
                _("You must either choose a material or fill in a custom material.")
            )

        return cleaned_data


class RateClassForm(forms.ModelForm):
    materials = forms.ModelMultipleChoiceField(
        queryset=Material.objects.all(),
        widget=FilteredSelectMultiple(verbose_name=_("materials"), is_stacked=False),
    )
    materials.label = _("Materials")
    materials.help_text = _(
        "Hold down “Control”, or “Command” on a Mac, to select more than one. "
        "A material can be in only one rate class, the materials you add to this"
        " rate class, will be removed from other rate classes."
    )

    class Meta:
        model = RateClass
        fields = ("name", "description", "rate")

    def __init__(self, *args, **kwargs):
        super(RateClassForm, self).__init__(*args, **kwargs)
        if self.instance:
            # fill initial related values
            self.fields["materials"].initial = self.instance.materials.all()
