from django.contrib import admin
from django.db.models import Count
from django.utils.translation import gettext_lazy as _

from adminsortable.admin import SortableAdmin
from sorl.thumbnail.admin import AdminInlineImageMixin

from booking.forms import EventForm, MaterialForm, MaterialAliasForm
from booking.models import ListViewFilter
from .models import (
    Category,
    Material,
    Event,
    MaterialImage,
    MaterialAlias,
    RateClass,
    Location,
)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        qs = super(CategoryAdmin, self).get_queryset(request)
        return qs.annotate(material_count=Count("materials"))

    def count_materials(self, obj):
        return obj.material_count

    count_materials.short_description = _("Number of materials")
    list_display = ("name", "description", "count_materials")


class MaterialImageInline(AdminInlineImageMixin, admin.StackedInline):
    model = MaterialImage


class MaterialAliasInline(admin.StackedInline):
    model = MaterialAlias


@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ("name", "location", "stock")
    list_filter = ["categories", "location", "gm", "lendable"]
    search_fields = ["name", "description"]
    form = MaterialForm
    inlines = [
        MaterialImageInline,
        MaterialAliasInline,
    ]


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    def booking_status(self, obj):
        return obj.booking_status

    booking_status.short_description = _("Booking status")
    list_display = (
        "name",
        "event_start",
        "event_end",
        "booking_status",
    )
    list_filter = ["visible"]
    search_fields = ["name"]
    prepopulated_fields = {"slug": ("name",)}
    form = EventForm


@admin.register(MaterialAlias)
class MaterialAliasAdmin(admin.ModelAdmin):
    list_display = ("name", "material")
    search_fields = ["name", "material__name"]
    form = MaterialAliasForm


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        qs = super(LocationAdmin, self).get_queryset(request)
        return qs.annotate(material_count=Count("materials"))

    def count_materials(self, obj):
        return obj.material_count

    count_materials.short_description = _("Number of materials")

    list_display = ("name", "count_materials")
    search_fields = ["name"]


@admin.register(RateClass)
class RateClassAdmin(admin.ModelAdmin):
    list_display = ("name", "description", "rate")
    search_fields = ["name"]


@admin.register(ListViewFilter)
class ListViewFilterAdmin(SortableAdmin):
    def get_included_categories(self, obj):
        return "\n".join([cat.name for cat in obj.included_categories.all()])

    def get_excluded_categories(self, obj):
        return "\n".join([cat.name for cat in obj.excluded_categories.all()])

    get_included_categories.short_description = _("Included categories")
    get_excluded_categories.short_description = _("Excluded categories")

    list_display = (
        "the_order",
        "name",
        "description",
        "enabled",
        "get_included_categories",
        "get_excluded_categories",
        "gm",
    )
