from django.contrib.auth.models import (
    AbstractUser,
    BaseUserManager,
    Group as DjangoGroup,
)
from django.db import models
from django.utils.translation import gettext_lazy as _

from users.models import Group


class UserManager(BaseUserManager):
    """Define a model manager for User model with no username field."""

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """Create and save a User with the given email and password."""
        if not email:
            raise ValueError("The given email must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular User with the given email and password."""
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    username = None
    email = models.EmailField(_("email address"), unique=True)
    # The custom group
    group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        help_text=_("What group should this user be associated with?"),
        verbose_name=_("group"),
    )
    # The authorization groups (renamed to roles)
    groups = models.ManyToManyField(
        DjangoGroup,
        verbose_name=_("roles"),
        blank=True,
        help_text=_(
            "The roles this user has. A user will get all permissions "
            "granted to each of their roles."
        ),
        related_name="user_set",
        related_query_name="user",
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.email

    @property
    def is_staff(self):
        return self.is_superuser or self.groups.filter(name="MB").exists()
