import csv, os

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from booking.models import Category, Material


class Command(BaseCommand):
    help = (
        "Imports the categories and the materials from the legacy dbase as initial data"
    )

    def add_arguments(self, parser):
        # No arguments
        pass

    @staticmethod
    def import_categories_and_materials():
        with transaction.atomic():

            ############################################################################
            # Import categories
            ############################################################################
            with open(
                os.path.join(
                    os.path.dirname(os.path.abspath(__file__)), "categorie.csv"
                )
            ) as csv_file:
                reader = csv.reader(csv_file, delimiter=",", quotechar='"')
                header = next(reader)

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

            ############################################################################
            # Import materials
            ############################################################################
            with open(
                os.path.join(
                    os.path.dirname(os.path.abspath(__file__)), "materiaal.csv",
                )
            ) as csv_file:
                reader = csv.reader(csv_file, delimiter=",", quotechar='"')
                header = next(reader)

                materials = []

                for row in reader:
                    name, description, category, gm, the_id = row
                    material = Material(
                        name=name, description=description, gm=(gm == "Ja"),
                    )
                    materials.append(material)
                    material.save()
                    material.categories.add(category_dict[category])

                return len(categories), len(materials)

    def handle(self, *args, **options):
        num_categories, num_materials = self.import_categories_and_materials()
        self.stdout.write(
            self.style.SUCCESS(
                "Successfully imported {} materials from {} categories.".format(
                    num_materials, num_categories
                )
            )
        )
