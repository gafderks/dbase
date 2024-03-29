# Generated by Django 3.1.1 on 2020-09-24 21:08

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0005_auto_20200921_2249"),
        ("booking", "0031_auto_20200921_2249"),
    ]

    operations = [
        migrations.AlterField(
            model_name="game",
            name="group",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to="users.group",
                verbose_name="group",
            ),
        ),
    ]
