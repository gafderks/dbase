# Generated by Django 3.0.4 on 2020-03-06 22:37

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("booking", "0013_auto_20200124_0713"),
    ]

    operations = [
        migrations.AddField(
            model_name="booking",
            name="custom_material",
            field=models.CharField(
                blank=True, max_length=150, null=True, verbose_name="custom material"
            ),
        ),
        migrations.AlterField(
            model_name="booking",
            name="requester",
            field=models.ForeignKey(
                editable=False,
                on_delete=django.db.models.deletion.DO_NOTHING,
                related_name="bookings",
                to=settings.AUTH_USER_MODEL,
                verbose_name="requester",
            ),
        ),
    ]
