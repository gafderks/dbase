from django.contrib import admin

from booking.forms import EventForm
from .models import Category, Material, Event, MaterialImage, MaterialAlias


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "description")


class MaterialImageInline(admin.StackedInline):
    model = MaterialImage
    readonly_fields = ["image_tag"]


class MaterialAliasInline(admin.StackedInline):
    model = MaterialAlias


@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ("name", "description")
    list_filter = ["categories"]
    search_fields = ["name"]
    inlines = [
        MaterialImageInline,
        MaterialAliasInline,
    ]


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_filter = ["visible"]
    search_fields = ["name"]
    form = EventForm
