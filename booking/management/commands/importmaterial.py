import csv, os

from django.core.management.base import BaseCommand
from django.db import transaction
from booking.models import Category, Material, Location


class Command(BaseCommand):
    help = (
        "Imports the categories and the materials from the legacy dbase as initial data"
    )

    LOCATIONS = [
        "Gang 1 (Decorattributen)",
        "Gang 2 (Sport en Spel)",
        "Gang 3 (Buitenartikelen)",
        "Geluidshok",
        "Kledingzolder",
    ]

    def add_arguments(self, parser):
        # No arguments
        pass

    @staticmethod
    def import_categories_and_materials():

        ################################################################################
        # Import categories
        ################################################################################
        with open(
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "categorie.csv")
        ) as csv_file:
            reader = csv.reader(csv_file, delimiter=",", quotechar='"')
            _ = next(reader)  # Skip the header

            categories = []
            category_dict = dict()

            for row in reader:
                the_id, name, description = row
                category, _ = Category.objects.get_or_create(
                    name=name, description=description
                )
                category.save()
                category_dict[the_id] = category
                categories.append(category)

        ################################################################################
        # Import materials
        ################################################################################
        with open(
            os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                "materiaal.csv",
            )
        ) as csv_file:
            reader = csv.reader(csv_file, delimiter=",", quotechar='"')
            _ = next(reader)  # Skip the header

            materials = []

            for row in reader:
                name, description, category, gm, the_id = row
                material = Material(
                    name=name,
                    description=description,
                    gm=(gm == "Ja"),
                )
                materials.append(material)
                material.save()
                material.categories.add(category_dict[category])

            return len(categories), len(materials)

    def import_locations(self):
        for location in self.LOCATIONS:
            location_object, _ = Location.objects.get_or_create(name=location)
            location_object.save()
        return len(self.LOCATIONS)

    def handle(self, *args, **options):
        with transaction.atomic():
            num_categories, num_materials = self.import_categories_and_materials()
            num_locations = self.import_locations()
        self.stdout.write(
            self.style.SUCCESS(
                "Successfully imported {} materials from {} categories and {} locations.".format(
                    num_materials, num_categories, num_locations
                )
            )
        )
