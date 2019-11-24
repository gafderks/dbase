from django.contrib import admin

from .models import Category, Material, Event


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')


class MaterialAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'category')
    list_filter = ['category']
    search_fields = ['name']


class EventAdmin(admin.ModelAdmin):
    list_filter = ['active', 'archived']
    search_fields = ['name']


admin.site.register(Category, CategoryAdmin)
admin.site.register(Material, MaterialAdmin)
admin.site.register(Event, EventAdmin)
