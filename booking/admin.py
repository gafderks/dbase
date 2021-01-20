from django.contrib import admin
from django.db.models import Count
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from adminsortable.admin import (
    SortableAdmin,
    NonSortableParentAdmin,
    SortableStackedInline,
)
from django_mptt_admin.admin import DjangoMpttAdmin
from mptt.admin import TreeRelatedFieldListFilter
from rules.contrib.admin import ObjectPermissionsModelAdmin
from sorl.thumbnail import get_thumbnail
from sorl.thumbnail.admin import AdminInlineImageMixin

from booking.forms import EventForm, MaterialForm, MaterialAliasForm, ListViewFilterForm
from booking.models import ListViewFilter
from .filters import HasMaterialImageListFilter
from .models import (
    Category,
    Material,
    Event,
    MaterialImage,
    MaterialAttachment,
    MaterialAlias,
    RateClass,
    Location,
)

ADMIN_THUMBS_SIZE = "60x60"


@admin.register(Category)
class CategoryAdmin(DjangoMpttAdmin):
    def get_queryset(self, request):
        qs = super(CategoryAdmin, self).get_queryset(request)
        return qs.annotate(material_count=Count("materials"))

    def count_materials(self, obj):
        return obj.material_count

    count_materials.short_description = _("Number of materials")
    list_display = ("__str__", "description", "count_materials")


class MaterialImageInline(AdminInlineImageMixin, SortableStackedInline):
    model = MaterialImage


class MaterialAttachmentInline(SortableStackedInline):
    model = MaterialAttachment


class MaterialAliasInline(admin.StackedInline):
    model = MaterialAlias


@admin.register(Material)
class MaterialAdmin(NonSortableParentAdmin):
    list_display = ("name", "thumbnail", "location", "stock")
    list_filter = [
        ("categories", TreeRelatedFieldListFilter),
        "location",
        "gm",
        "lendable",
        HasMaterialImageListFilter,
    ]
    search_fields = ["name", "description", "aliases__name"]
    fields = (
        "name",
        "description",
        "categories",
        "gm",
        "lendable",
        "location",
        "rate_class",
        ("stock_value", "stock_unit"),
    )
    form = MaterialForm
    inlines = [MaterialImageInline, MaterialAliasInline, MaterialAttachmentInline]
    save_on_top = True
    change_list_template = "camera/material_change_list_camera_button.html"

    def thumbnail(self, obj):
        html = []
        for img in obj.images.all():
            thumb = get_thumbnail(img.image, ADMIN_THUMBS_SIZE, crop="center")
            full_size = img.image.url

            html.append(
                '<a href="{}" target="_blank"><img width="{}" src="{}" /></a>'.format(
                    full_size, thumb.width, thumb.url
                )
            )
        return format_html("&nbsp;".join(html))

    thumbnail.short_description = _("Image")


@admin.register(Event)
class EventAdmin(ObjectPermissionsModelAdmin):
    def booking_status(self, obj):
        return obj.booking_status.label

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

    def get_queryset(self, request):
        """
        Return only the viewable events.
        """
        return Event.objects.viewable(request.user)


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
    form = ListViewFilterForm
