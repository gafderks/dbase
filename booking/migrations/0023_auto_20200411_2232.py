# Generated by Django 3.0.5 on 2020-04-11 20:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("booking", "0022_auto_20200411_2145"),
    ]

    operations = [
        migrations.AlterField(
            model_name="material",
            name="stock_value",
            field=models.FloatField(
                blank=True,
                help_text="How many exemplars are there of this material?",
                null=True,
                verbose_name="stock value",
            ),
        ),
    ]
