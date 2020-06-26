# Generated by Django 3.0.1 on 2019-12-31 13:30

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import users.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [("auth", "__latest__")]

    operations = [
        migrations.CreateModel(
            name="Group",
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
                ("name", models.CharField(max_length=250, unique=True)),
                (
                    "type",
                    models.CharField(
                        choices=[("GR", "Group"), ("CO", "Commission")],
                        default="CO",
                        help_text="What type is the group?",
                        max_length=2,
                        verbose_name="type",
                    ),
                ),
            ],
            options={
                "verbose_name": "group",
                "verbose_name_plural": "groups",
                "ordering": ["name"],
            },
        ),
        migrations.CreateModel(
            name="User",
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
                ("password", models.CharField(max_length=128, verbose_name="password")),
                (
                    "last_login",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="last login"
                    ),
                ),
                (
                    "is_superuser",
                    models.BooleanField(
                        default=False,
                        help_text="Designates that this user has all permissions without explicitly assigning them.",
                        verbose_name="superuser status",
                    ),
                ),
                (
                    "first_name",
                    models.CharField(
                        blank=True, max_length=30, verbose_name="first name"
                    ),
                ),
                (
                    "last_name",
                    models.CharField(
                        blank=True, max_length=150, verbose_name="last name"
                    ),
                ),
                (
                    "is_active",
                    models.BooleanField(
                        default=True,
                        help_text="Designates whether this user should be treated as active. Unselect this instead of deleting accounts.",
                        verbose_name="active",
                    ),
                ),
                (
                    "date_joined",
                    models.DateTimeField(
                        default=django.utils.timezone.now, verbose_name="date joined"
                    ),
                ),
                (
                    "email",
                    models.EmailField(
                        max_length=254, unique=True, verbose_name="email address"
                    ),
                ),
                (
                    "group",
                    models.ForeignKey(
                        blank=True,
                        help_text="What group should this user be associated with?",
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        to="users.Group",
                        verbose_name="group",
                    ),
                ),
                (
                    "groups",
                    models.ManyToManyField(
                        blank=True,
                        help_text="The roles this user has. A user will get all permissions granted to each of their roles.",
                        related_name="user_set",
                        related_query_name="user",
                        to="auth.Group",
                        verbose_name="roles",
                    ),
                ),
                (
                    "user_permissions",
                    models.ManyToManyField(
                        blank=True,
                        help_text="Specific permissions for this user.",
                        related_name="user_set",
                        related_query_name="user",
                        to="auth.Permission",
                        verbose_name="user permissions",
                    ),
                ),
            ],
            options={
                "verbose_name": "user",
                "verbose_name_plural": "users",
                "abstract": False,
            },
            managers=[("objects", users.models.UserManager()),],
        ),
    ]
