from django.core.management.base import BaseCommand
from tempfile import TemporaryDirectory
from shutil import copyfile
import pathlib

from django.utils.text import slugify

from booking.models import Material


class Command(BaseCommand):
    help = "Exports the material images for downloading"

    def add_arguments(self, parser):
        # No arguments
        pass

    @staticmethod
    def export_images(export_dir):
        export_dir = pathlib.Path(export_dir)
        materials = Material.objects.prefetch_related("images").all()

        for material in materials:
            for i, image in enumerate(material.images.all()):
                origin = pathlib.Path(image.image.path)
                if i == 0:
                    suffix = origin.suffix
                else:
                    suffix = "" ".{}{}".format(i, origin.suffix)
                copyfile(
                    origin, (export_dir / slugify(material.name)).with_suffix(suffix)
                )

    def handle(self, *args, **options):

        with TemporaryDirectory() as export_dir:
            self.stdout.write("Exporting images...")
            self.export_images(export_dir)
            input(
                "Download the images from {} and press a key afterwards".format(
                    export_dir
                )
            )
