from django.contrib.auth.models import AbstractUser, BaseUserManager, Group as DjangoGroup, PermissionsMixin
from django.db import models
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
    """Define a model manager for User model with no username field."""

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """Create and save a User with the given email and password."""
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular User with the given email and password."""
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


class Role(DjangoGroup):
    """Rename Django Groups to Roles for distinguishing from custom Group definition"""
    class Meta:
        proxy = True
        app_label = 'auth'
        verbose_name = _('role')
        verbose_name_plural = _('roles')


class Group(models.Model):
    name = models.CharField(max_length=250, unique=True)
    GROUP = 'GR'
    COMMISSION = 'CO'
    GROUP_TYPE_CHOICES = [
        (GROUP, _('Group')),
        (COMMISSION, _('Commission')),
    ]
    type = models.CharField(
        max_length=2,
        choices=GROUP_TYPE_CHOICES,
        default=COMMISSION,
        verbose_name=_('type'),
        help_text=_('What type is the group?')
    )

    class Meta:
        verbose_name = _('group')
        verbose_name_plural = _('groups')

    def __str__(self):
        return self.name


class User(AbstractUser):
    username = None
    email = models.EmailField(_('email address'), unique=True)
    # The custom group
    group = models.ForeignKey(Group, on_delete=models.DO_NOTHING, blank=True, null=True,
                              help_text=_('What group should this user be associated with?'),
                              verbose_name=_('group'))
    # The authorization groups (renamed to roles)
    groups = models.ManyToManyField(
        DjangoGroup,
        verbose_name=_('roles'),
        blank=True,
        help_text=_(
            'The roles this user has. A user will get all permissions '
            'granted to each of their roles.'
        ),
        related_name="user_set",
        related_query_name="user",
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.email
