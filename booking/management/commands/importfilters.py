from django.core.management.base import BaseCommand
from django.db import transaction
from booking.models import ListViewFilter, Category


class Command(BaseCommand):
    help = "Imports the default list view filters"

    def add_arguments(self, parser):
        # No arguments
        pass

    FILTERS = [
        {
            "name": "GM Non-food",
            "description": "Lucht, kramen, dranghekken, banken, enz.",
            "included_categories": [],
            "excluded_categories": [Category.objects.get(name="Food")],
            "gm": True,
        },
        {
            "name": "GM Food",
            "description": "Drank, ijs, appels, enz.",
            "included_categories": [Category.objects.get(name="Food")],
            "excluded_categories": [],
            "gm": True,
        },
        {
            "name": "Apparaten",
            "description": "Rook, mobiel geluid, enz.",
            "included_categories": [Category.objects.get(name="Licht en geluid")],
            "excluded_categories": [],
            "gm": False,
        },
    ]

    def import_filters(self):
        for list_view_filter in self.FILTERS:
            filter_object, _ = ListViewFilter.objects.get_or_create(
                name=list_view_filter["name"],
                description=list_view_filter["description"],
                gm=list_view_filter["gm"],
            )
            filter_object.save()
            for category in list_view_filter["included_categories"]:
                filter_object.included_categories.add(category)
            for category in list_view_filter["excluded_categories"]:
                filter_object.excluded_categories.add(category)
        return len(self.FILTERS)

    def handle(self, *args, **options):
        with transaction.atomic():
            num_filters = self.import_filters()
        self.stdout.write(
            self.style.SUCCESS(
                "Successfully imported {} list view filters.".format(num_filters)
            )
        )
