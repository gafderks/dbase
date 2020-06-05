from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.text import slugify

from users.models import Group
from django.contrib.auth.models import Group as DjangoGroup
from django.contrib.auth.models import Permission


class Command(BaseCommand):
    help = "Imports a set of predefined roles and groups"

    GROUPS = [
        {"name": "Groep 1-2N", "type": Group.GROUP},
        {"name": "Groep 1-2H", "type": Group.GROUP},
        {"name": "Groep 3-4", "type": Group.GROUP},
        {"name": "Groep 5-6", "type": Group.GROUP},
        {"name": "Groep 7-8", "type": Group.GROUP},
        {"name": "Groep 7-8", "type": Group.GROUP},
        {"name": "WS groep 3-4", "type": Group.GROUP},
        {"name": "WS groep 5-6-7-8", "type": Group.GROUP},
        {"name": "COS", "type": Group.COMMISSION},
        {"name": "Feestzaal", "type": Group.COMMISSION},
        {"name": "Leidingactiviteit", "type": Group.COMMISSION},
        {"name": "Kinderactiviteit", "type": Group.COMMISSION},
    ]

    ROLES = [
        {
            "name": "MB",
            "permissions": [
                # "change_other_groups_bookings",
                "view_others_groups_bookings",
                "view_category",
                "book_on_privileged_events",
                "view_event",
                "view_location",
                "add_material",
                "change_material",
                "delete_material",
                "view_material",
                "add_materialalias",
                "change_materialalias",
                "delete_materialalias",
                "view_materialalias",
                "add_materialimage",
                "change_materialimage",
                "delete_materialimage",
                "view_materialimage",
                "view_rateclass",
            ],
        }
    ]

    def add_arguments(self, parser):
        # No arguments
        pass

    def create_roles(self):
        with transaction.atomic():
            for role in self.ROLES:
                role_object, _ = DjangoGroup.objects.get_or_create(name=role["name"])
                for perm in role["permissions"]:
                    role_object.permissions.add(Permission.objects.get(codename=perm))
                role_object.save()
            return len(self.ROLES)

    def create_groups(self):
        with transaction.atomic():
            for group in self.GROUPS:
                group_object, _ = Group.objects.get_or_create(
                    name=group["name"], type=group["type"], slug=slugify(group["name"])
                )
                group_object.save()
            return len(self.GROUPS)

    def handle(self, *args, **options):
        num_groups = self.create_groups()
        num_roles = self.create_roles()
        self.stdout.write(
            self.style.SUCCESS(
                "Successfully imported {} groups and {} roles.".format(
                    num_groups, num_roles
                )
            )
        )
