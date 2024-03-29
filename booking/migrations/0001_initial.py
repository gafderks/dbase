# Generated by Django 3.0.1 on 2019-12-31 13:30

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Booking",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "day",
                    models.DateField(
                        help_text="On what day are the materials needed?",
                        verbose_name="day",
                    ),
                ),
                (
                    "part_of_day",
                    models.CharField(
                        choices=[
                            ("MO", "Morning"),
                            ("AF", "Afternoon"),
                            ("EV", "Evening"),
                            ("NI", "Night"),
                            ("DA", "Day"),
                        ],
                        default="MO",
                        help_text="At what part of the day are the materials needed?",
                        max_length=2,
                        verbose_name="part of day",
                    ),
                ),
                (
                    "workweek",
                    models.CharField(
                        blank=True, max_length=150, null=True, verbose_name="workweek"
                    ),
                ),
                (
                    "comment",
                    models.CharField(
                        blank=True, max_length=250, null=True, verbose_name="comment"
                    ),
                ),
                ("amount", models.CharField(max_length=150, verbose_name="amount")),
            ],
            options={
                "verbose_name": "booking",
                "verbose_name_plural": "bookings",
                "permissions": [
                    (
                        "can_change_other_groups_bookings",
                        "Can change bookings of other groups",
                    ),
                    (
                        "can_view_others_groups_bookings",
                        "Can view bookings of other groups",
                    ),
                ],
            },
        ),
        migrations.CreateModel(
            name="Category",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=150, verbose_name="name")),
                (
                    "description",
                    models.CharField(
                        blank=True, max_length=250, verbose_name="description"
                    ),
                ),
            ],
            options={
                "verbose_name": "category",
                "verbose_name_plural": "categories",
            },
        ),
        migrations.CreateModel(
            name="Event",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=150, verbose_name="name")),
                (
                    "locked",
                    models.BooleanField(
                        default=False,
                        help_text="Manually lock the booking such that users cannot change bookings (except admin).",
                        verbose_name="locked",
                    ),
                ),
                (
                    "visible",
                    models.BooleanField(
                        default=True,
                        help_text="Should the event be visible?",
                        verbose_name="visible",
                    ),
                ),
                (
                    "booking_start",
                    models.DateTimeField(
                        help_text="When should the event be opened for booking?",
                        verbose_name="start date booking period",
                    ),
                ),
                (
                    "booking_end",
                    models.DateTimeField(
                        help_text="When should the event become privileged?",
                        verbose_name="end date booking period",
                    ),
                ),
                (
                    "privileged_booking_end",
                    models.DateTimeField(
                        help_text="When should the event become locked?",
                        verbose_name="end date privileged booking period",
                    ),
                ),
                (
                    "event_start",
                    models.DateField(
                        help_text="What is the first day of the event?",
                        verbose_name="event start date",
                    ),
                ),
                (
                    "event_end",
                    models.DateField(
                        help_text="What is the last day of the event?",
                        verbose_name="event end date",
                    ),
                ),
            ],
            options={
                "verbose_name": "event",
                "verbose_name_plural": "events",
                "ordering": ["-event_end"],
                "permissions": [
                    ("can_view_hidden_events", "Can view hidden events"),
                    ("can_change_privileged_events", "Can change privileged events"),
                    ("can_change_locked_events", "Can change locked events"),
                ],
                "get_latest_by": "event_end",
            },
        ),
        migrations.CreateModel(
            name="Game",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=250, verbose_name="name")),
                (
                    "order",
                    models.PositiveIntegerField(
                        editable=False,
                        help_text="Defines an ordering for the games within a day/part of day",
                        verbose_name="order",
                    ),
                ),
                (
                    "day",
                    models.DateField(
                        help_text="On what day are the materials needed?",
                        verbose_name="day",
                    ),
                ),
                (
                    "part_of_day",
                    models.CharField(
                        choices=[
                            ("MO", "Morning"),
                            ("AF", "Afternoon"),
                            ("EV", "Evening"),
                            ("NI", "Night"),
                            ("DA", "Day"),
                        ],
                        default="MO",
                        help_text="At what part of the day are the materials needed?",
                        max_length=2,
                        verbose_name="part of day",
                    ),
                ),
            ],
            options={
                "verbose_name": "game",
                "verbose_name_plural": "games",
            },
        ),
        migrations.CreateModel(
            name="Location",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=150, verbose_name="name")),
            ],
            options={
                "verbose_name": "location",
                "verbose_name_plural": "locations",
            },
        ),
        migrations.CreateModel(
            name="Material",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "name",
                    models.CharField(max_length=150, unique=True, verbose_name="name"),
                ),
                (
                    "description",
                    models.CharField(
                        blank=True, max_length=250, verbose_name="description"
                    ),
                ),
                (
                    "gm",
                    models.BooleanField(
                        help_text="Is GM needed for this material?", verbose_name="GM"
                    ),
                ),
                (
                    "lendable",
                    models.BooleanField(
                        default=True,
                        help_text="Should this material be shown for lending?",
                        verbose_name="lendable",
                    ),
                ),
                (
                    "stock",
                    models.CharField(
                        blank=True,
                        help_text="How many exemplars are there of this material?",
                        max_length=150,
                        verbose_name="stock",
                    ),
                ),
                ("categories", models.ManyToManyField(to="booking.Category")),
                (
                    "location",
                    models.ForeignKey(
                        blank=True,
                        help_text="Where can this material be found?",
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        to="booking.Location",
                        verbose_name="location",
                    ),
                ),
            ],
            options={
                "verbose_name": "material",
                "verbose_name_plural": "materials",
            },
        ),
        migrations.CreateModel(
            name="RateClass",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=150, verbose_name="name")),
                (
                    "description",
                    models.CharField(
                        blank=True, max_length=250, verbose_name="description"
                    ),
                ),
                (
                    "rate",
                    models.DecimalField(
                        decimal_places=2, max_digits=5, verbose_name="rate"
                    ),
                ),
            ],
            options={
                "verbose_name": "rate class",
                "verbose_name_plural": "rate classes",
            },
        ),
        migrations.CreateModel(
            name="MaterialImage",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "image",
                    models.ImageField(upload_to="materials", verbose_name="image"),
                ),
                (
                    "material",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="images",
                        to="booking.Material",
                        verbose_name="material",
                    ),
                ),
            ],
            options={
                "verbose_name": "material image",
                "verbose_name_plural": "material images",
            },
        ),
        migrations.CreateModel(
            name="MaterialAlias",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        help_text='Alias for the material, e.g. aliases for "stormbaan" are "Kelly" and "Rambler".',
                        max_length=150,
                        unique=True,
                        verbose_name="name",
                    ),
                ),
                (
                    "material",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        to="booking.Material",
                        verbose_name="material",
                    ),
                ),
            ],
            options={
                "verbose_name": "material alias",
                "verbose_name_plural": "material aliases",
            },
        ),
        migrations.AddField(
            model_name="material",
            name="rate_class",
            field=models.ForeignKey(
                blank=True,
                help_text="What rate class should this material be associated with?",
                null=True,
                on_delete=django.db.models.deletion.DO_NOTHING,
                to="booking.RateClass",
                verbose_name="rate class",
            ),
        ),
    ]
