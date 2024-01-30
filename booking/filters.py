import copy

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Field, Submit, HTML
from django.contrib import admin
from django.db.models import Count
from django.forms import NullBooleanSelect, NullBooleanField
from django.utils.choices import CallableChoiceIterator
from django.utils.translation import gettext as __
from django.utils.translation import gettext_lazy as _
from django_filters import BooleanFilter, ChoiceFilter, FilterSet, ModelChoiceFilter
from mptt.forms import TreeNodeChoiceField

from booking.models import Category, Booking, Material


class CustomNullBooleanSelect(NullBooleanSelect):
    def __init__(
        self,
        attrs=None,
        choices=(),
    ):
        super().__init__(attrs)
        self.choices = list(choices)


class CustomNullBooleanField(NullBooleanField):
    widget = CustomNullBooleanSelect

    def __init__(self, *args, choices=(), **kwargs):
        super().__init__(*args, **kwargs)
        self.choices = choices

    def __deepcopy__(self, memo):
        result = super().__deepcopy__(memo)
        result._choices = copy.deepcopy(self._choices, memo)
        return result

    def _get_choices(self):
        return self._choices

    def _set_choices(self, value):
        # Setting choices also sets the choices on the widget.
        # choices can be any iterable, but we call list() on it because
        # it will be consumed more than once.
        if callable(value):
            value = CallableChoiceIterator(value)
        else:
            value = list(value)

        self._choices = self.widget.choices = value

    choices = property(_get_choices, _set_choices)


class CustomBooleanFilter(BooleanFilter):
    """
    Adds the functionality to specify choices for the BooleanFilter.
    Choices must be 'unknown', 'true', and 'false', but labels can be customized.
    """

    field_class = CustomNullBooleanField

    def __init__(
        self,
        *args,
        choices=(
            ("unknown", _("Any")),
            ("true", _("Yes")),
            ("false", _("No")),
        ),
        **kwargs,
    ):
        super().__init__(*args, choices=choices, **kwargs)


class BookingFilter(FilterSet):
    categories = ModelChoiceFilter(
        field_name="material__categories",
        queryset=Category.objects.all(),
        label=_("Category"),
        empty_label=_("----------"),
    )
    is_custom_material = CustomBooleanFilter(
        field_name="custom_material",
        label=_("Custom material"),
        lookup_expr="isnull",
        exclude=True,
        choices=(
            ("unknown", _("----------")),
            ("true", _("Only custom materials")),
            ("false", _("No custom materials")),
        ),
    )
    gm = ChoiceFilter(
        field_name="material__gm",
        label=_("GM"),
        empty_label=None,
        choices=(
            ("", _("----------")),
            (True, _("GM needed")),
            (False, _("GM not needed")),
        ),
    )
    workweek = ChoiceFilter(
        field_name="workweek",
        label=_("Workweek"),
        empty_label=None,
        choices=(
            ("", _("----------")),
            (True, _("Needed in workweek")),
            (False, _("Not needed in workweek")),
        ),
    )

    @property
    def is_active(self):
        """
        Returns whether any filter is active.
        :return bool:
        """
        return len(self.active_filters) > 0

    @property
    def active_filters(self):
        """
        Returns a list with the filters that are active.
        :return list[str]:
        """
        if not self.form.is_valid():
            return []
        return [
            f
            for f in self.filters.keys()
            if self.form.cleaned_data and self.form.cleaned_data[f] not in ("", None)
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        helper = FormHelper()
        helper.layout = Layout(
            Div(
                Field(
                    "gm",
                    template="crispy/floating-labels.html",
                    wrapper_class="col-12 col-md-6 col-lg px-1 mb-lg-0",
                    title=(
                        __("GM") + " (" + __("active") + ")"
                        if "gm" in self.active_filters
                        else __("GM")
                    ),
                    css_class="filter-active" if "gm" in self.active_filters else "",
                ),
                Field(
                    "workweek",
                    template="crispy/floating-labels.html",
                    wrapper_class="col-12 col-md-6 col-lg px-1 mb-lg-0",
                    title=(
                        __("Workweek") + " (" + __("active") + ")"
                        if "workweek" in self.active_filters
                        else __("Workweek")
                    ),
                    css_class=(
                        "filter-active" if "workweek" in self.active_filters else ""
                    ),
                ),
                Field(
                    "categories",
                    template="crispy/floating-labels.html",
                    wrapper_class="col-12 col-md-6 col-lg px-1 mb-lg-0",
                    title=(
                        __("Categories") + " (" + __("active") + ")"
                        if "categories" in self.active_filters
                        else __("Categories")
                    ),
                    css_class=(
                        "filter-active" if "categories" in self.active_filters else ""
                    ),
                ),
                Field(
                    "is_custom_material",
                    template="crispy/floating-labels.html",
                    wrapper_class="col-12 col-md-6 col-lg px-1 mb-lg-0",
                    title=(
                        __("Custom material") + " (" + __("active") + ")"
                        if "is_custom_material" in self.active_filters
                        else __("Custom material")
                    ),
                    css_class=(
                        "filter-active"
                        if "is_custom_material" in self.active_filters
                        else ""
                    ),
                ),
                Div(
                    Submit(
                        "filter",
                        _("Apply filters"),
                        css_class="btn-secondary",
                    ),
                    HTML(
                        '<a href="?" class="btn btn-outline-secondary">{}</a>'.format(
                            _("Clear")
                        )
                    ),
                    css_class="col-12 col-lg-auto px-1 mb-xl-0 form-label-group mb-md-0",
                ),
                css_class="row mx-0",
            ),
        )
        helper.form_class = "form-inline"
        helper.disable_csrf = True
        self.helper = helper

    class Meta:
        model = Booking
        fields = []


class HasMaterialImageListFilter(admin.SimpleListFilter):
    """
    Filter for materials on whether they have images or not.
    """

    title = _("has image")

    # Parameter for the filter that will be used in the URL query.
    parameter_name = "has_image"

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        return (
            ("true", _("Yes")),
            ("false", _("No")),
        )

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        queryset = queryset.annotate(image_count=Count("images"))
        if self.value() == "true":
            return queryset.filter(image_count__gt=0)
        if self.value() == "false":
            return queryset.filter(image_count=0)


class TreeNodeChoiceFilter(ModelChoiceFilter):
    """Idea from https://github.com/carltongibson/django-filter/issues/123#issuecomment-675502695"""

    field_class = TreeNodeChoiceField

    def filter(self, qs, value):
        if value != self.null_value and value is not None:
            return self.get_method(qs)(
                **{f"{self.field_name}__in": value.get_descendants(include_self=True)}
            )
        return qs.distinct() if self.distinct else qs


class MaterialCategoryFilter(FilterSet):
    categories = TreeNodeChoiceFilter(
        field_name="categories",
        queryset=Category.objects.all(),
        label=_("Category"),
        empty_label=_("----------"),
    )

    def __init__(self, *args, **kwargs):
        wrapper_class = kwargs.pop("wrapper_class", "")
        super().__init__(*args, **kwargs)
        helper = FormHelper()
        helper.layout = Layout(
            Div(
                Field(
                    "categories",
                    template="crispy/category-buttons.html",
                    wrapper_class=wrapper_class,
                ),
            ),
        )
        helper.form_class = "form-inline"
        helper.disable_csrf = True
        helper.form_show_labels = False
        self.helper = helper

    class Meta:
        model = Material
        fields = []
