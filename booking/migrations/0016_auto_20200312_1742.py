# Generated by Django 3.0.4 on 2020-03-12 16:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("booking", "0015_auto_20200312_1738"),
    ]

    operations = [
        migrations.AlterField(
            model_name="listviewfilter",
            name="enabled",
            field=models.BooleanField(default=True, verbose_name="Enabled"),
        ),
    ]
