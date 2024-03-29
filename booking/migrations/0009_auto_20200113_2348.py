# Generated by Django 3.0.1 on 2020-01-13 22:48

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("booking", "0008_auto_20200112_1907"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="game",
            options={
                "ordering": ("order",),
                "verbose_name": "game",
                "verbose_name_plural": "games",
            },
        ),
        migrations.AddField(
            model_name="game",
            name="order",
            field=models.PositiveIntegerField(
                db_index=True, default=1, editable=False, verbose_name="order"
            ),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="game",
            name="part_of_day",
            field=models.CharField(
                choices=[
                    ("DA", "Day"),
                    ("MO", "Morning"),
                    ("AF", "Afternoon"),
                    ("EV", "Evening"),
                    ("NI", "Night"),
                ],
                default="MO",
                help_text="At what part of the day are the materials needed?",
                max_length=2,
                verbose_name="part of day",
            ),
        ),
        migrations.AlterField(
            model_name="partofday",
            name="part_of_day_code",
            field=models.CharField(
                choices=[
                    ("DA", "Day"),
                    ("MO", "Morning"),
                    ("AF", "Afternoon"),
                    ("EV", "Evening"),
                    ("NI", "Night"),
                ],
                default="MO",
                help_text="At what part of the day are the materials needed?",
                max_length=2,
                verbose_name="part of day",
            ),
        ),
    ]
