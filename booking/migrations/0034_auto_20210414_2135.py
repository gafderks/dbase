# Generated by Django 3.2 on 2021-04-14 19:35

from django.db import migrations, models
import mptt.fields


class Migration(migrations.Migration):
    dependencies = [
        ("booking", "0033_auto_20210119_2244"),
    ]

    operations = [
        migrations.AlterField(
            model_name="booking",
            name="id",
            field=models.BigAutoField(
                auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
            ),
        ),
        migrations.AlterField(
            model_name="category",
            name="id",
            field=models.BigAutoField(
                auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
            ),
        ),
        migrations.AlterField(
            model_name="event",
            name="id",
            field=models.BigAutoField(
                auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
            ),
        ),
        migrations.AlterField(
            model_name="game",
            name="id",
            field=models.BigAutoField(
                auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
            ),
        ),
        migrations.AlterField(
            model_name="listviewfilter",
            name="excluded_categories",
            field=mptt.fields.TreeManyToManyField(
                blank=True,
                help_text="Materials from these categories and their subcategories will <strong>not</strong> be part of the list.",
                related_name="_booking_listviewfilter_excluded_categories_+",
                to="booking.Category",
                verbose_name="excluded categories",
            ),
        ),
        migrations.AlterField(
            model_name="listviewfilter",
            name="gm",
            field=models.BooleanField(
                help_text="Setting <em>Unknown</em> disables the condition.",
                null=True,
                verbose_name="GM",
            ),
        ),
        migrations.AlterField(
            model_name="listviewfilter",
            name="id",
            field=models.BigAutoField(
                auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
            ),
        ),
        migrations.AlterField(
            model_name="listviewfilter",
            name="included_categories",
            field=mptt.fields.TreeManyToManyField(
                blank=True,
                help_text="Materials from these categories and their subcategories will be part of the list.",
                related_name="_booking_listviewfilter_included_categories_+",
                to="booking.Category",
                verbose_name="included categories",
            ),
        ),
        migrations.AlterField(
            model_name="location",
            name="id",
            field=models.BigAutoField(
                auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
            ),
        ),
        migrations.AlterField(
            model_name="material",
            name="categories",
            field=mptt.fields.TreeManyToManyField(
                related_name="materials", to="booking.Category"
            ),
        ),
        migrations.AlterField(
            model_name="material",
            name="id",
            field=models.BigAutoField(
                auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
            ),
        ),
        migrations.AlterField(
            model_name="materialalias",
            name="id",
            field=models.BigAutoField(
                auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
            ),
        ),
        migrations.AlterField(
            model_name="materialattachment",
            name="id",
            field=models.BigAutoField(
                auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
            ),
        ),
        migrations.AlterField(
            model_name="materialimage",
            name="id",
            field=models.BigAutoField(
                auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
            ),
        ),
        migrations.AlterField(
            model_name="partofday",
            name="id",
            field=models.BigAutoField(
                auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
            ),
        ),
        migrations.AlterField(
            model_name="rateclass",
            name="id",
            field=models.BigAutoField(
                auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
            ),
        ),
    ]
