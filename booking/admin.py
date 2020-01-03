from django.contrib import admin
from django.db.models import Count
from django.utils.translation import gettext_lazy as _

from booking.forms import EventForm, MaterialForm, MaterialAliasForm
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


class MaterialImageInline(admin.StackedInline):
    model = MaterialImage
    readonly_fields = ["image_tag"]


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
