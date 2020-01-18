# Generated by Django 3.0.1 on 2020-01-12 17:35

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("booking", "0006_auto_20200104_1741"),
    ]

    operations = [
        migrations.RemoveField(model_name="game", name="order",),
        migrations.AlterField(
            model_name="game",
            name="creator",
            field=models.ForeignKey(
                editable=False,
                on_delete=django.db.models.deletion.DO_NOTHING,
                related_name="games",
                to=settings.AUTH_USER_MODEL,
                verbose_name="creator",
            ),
        ),
        migrations.AlterField(
            model_name="game",
            name="name",
            field=models.CharField(max_length=250, verbose_name="Game name"),
        ),
    ]
