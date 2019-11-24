from django.db import models
from django.utils.translation import gettext_lazy as _


class Category(models.Model):
    name = models.CharField(verbose_name=_('name'), max_length=150)
    description = models.CharField(verbose_name=_('description'), max_length=250, blank=True)

    class Meta:
        verbose_name = _('category')
        verbose_name_plural = _('categories')

    def __str__(self):
        return self.name


class Material(models.Model):
    name = models.CharField(verbose_name=_('name'), max_length=150)
    description = models.CharField(verbose_name=_('description'), max_length=250, blank=True)
    category = models.ForeignKey(Category, on_delete=models.DO_NOTHING, blank=True, null=True)
    gm = models.BooleanField(verbose_name=_('GM'))
    image = models.ImageField(verbose_name=_('image'), blank=True)

    class Meta:
        verbose_name = _('material')
        verbose_name_plural = _('materials')

    def __str__(self):
        return self.name


class MaterialAlias(models.Model):
    name = models.CharField(verbose_name=_('name'), max_length=150)
    material = models.ForeignKey(Material, on_delete=models.DO_NOTHING)

    class Meta:
        verbose_name = _('material alias')
        verbose_name_plural = _('material aliases')

    def __str__(self):
        return self.name


class Game(models.Model):
    name = models.CharField(max_length=250)
    order = models.PositiveIntegerField()
    day = models.DateField()
    MORNING = 'MO'
    AFTERNOON = 'AF'
    EVENING = 'EV'
    DAY = 'DA'
    NIGHT = 'NI'
    PART_OF_DAY_CHOICES = [
        (MORNING, _('Morning')),
        (AFTERNOON, _('Afternoon')),
        (EVENING, _('Evening')),
        (NIGHT, _('Night')),
        (DAY, _('Day'))
    ]
    part_of_day = models.CharField(
        max_length=2,
        choices=PART_OF_DAY_CHOICES,
        default=MORNING,
    )

    class Meta:
        verbose_name = _('game')
        verbose_name_plural = _('games')

    def __str__(self):
        return self.name


class Group(models.Model):
    name = models.CharField(max_length=250)

    class Meta:
        verbose_name = _('group')
        verbose_name_plural = _('groups')

    def __str__(self):
        return self.name


class Event(models.Model):
    name = models.CharField(max_length=150)
    active = models.BooleanField()
    archived = models.BooleanField()
    booking_start = models.DateTimeField()
    booking_end = models.DateTimeField()
    event_start = models.DateField()
    event_end = models.DateField()

    class Meta:
        verbose_name = _('event')
        verbose_name_plural = _('events')
        get_latest_by = "event_start"

    def __str__(self):
        return self.name


class Booking(models.Model):
    group = models.ForeignKey(Group, on_delete=models.DO_NOTHING)
    day = models.CharField(max_length=150)
    part_of_day = models.CharField(max_length=150)
    game = models.ForeignKey(Game, on_delete=models.DO_NOTHING, null=True)
    material = models.ForeignKey(Material, on_delete=models.DO_NOTHING)
    workweek = models.CharField(max_length=150, blank=True, null=True)
    comment = models.CharField(max_length=250, blank=True, null=True)
    amount = models.CharField(max_length=150)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)

    class Meta:
        verbose_name = _('booking')
        verbose_name_plural = _('bookings')

    def __str__(self):
        return self.material.name


class User(models.Model):
    username = models.CharField(primary_key=True, max_length=250)
    password = models.CharField(max_length=250)
    name = models.CharField(max_length=250)
