from django.contrib import admin

from .models import Category, Material, Event, MaterialImage, MaterialAlias


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')


class MaterialImageInline(admin.StackedInline):
    model = MaterialImage


class MaterialAliasInline(admin.StackedInline):
    model = MaterialAlias


class MaterialAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    list_filter = ['category']
    search_fields = ['name']
    inlines = [
        MaterialImageInline,
        MaterialAliasInline,
    ]


class EventAdmin(admin.ModelAdmin):
    list_filter = ['active', 'archived']
    search_fields = ['name']


admin.site.register(Category, CategoryAdmin)
admin.site.register(Material, MaterialAdmin)
admin.site.register(Event, EventAdmin)
