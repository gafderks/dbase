# Generated by Django 3.0.1 on 2019-12-29 20:25

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('booking', '0003_auto_20191229_1924'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='event',
            name='active',
        ),
        migrations.RemoveField(
            model_name='event',
            name='archived',
        ),
        migrations.RemoveField(
            model_name='event',
            name='privileged',
        ),
        migrations.AddField(
            model_name='event',
            name='privileged_booking_end',
            field=models.DateTimeField(default=django.utils.timezone.now, help_text='When should the event become locked?'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='event',
            name='visible',
            field=models.BooleanField(default=True, help_text='Should the event be visible?'),
        ),
        migrations.AlterField(
            model_name='event',
            name='locked',
            field=models.BooleanField(default=False, help_text='Manually lock the booking such that users cannot change bookings (except admin).'),
        ),
    ]
