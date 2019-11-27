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


class RateClass(models.Model):
    name = models.CharField(verbose_name=_('name'), max_length=150)
    description = models.CharField(verbose_name=_('description'), max_length=250, blank=True)
    rate = models.DecimalField(verbose_name=_('rate'), decimal_places=2, max_digits=5)

    class Meta:
        verbose_name = _('rate class')
        verbose_name_plural = _('rate classes')

    def __str__(self):
        return self.name


class Location(models.Model):
    name = models.CharField(verbose_name=_('name'), max_length=150)

    class Meta:
        verbose_name = _('location')
        verbose_name_plural = _('locations')

    def __str__(self):
        return self.name


class Material(models.Model):
    name = models.CharField(verbose_name=_('name'), max_length=150)
    description = models.CharField(verbose_name=_('description'), max_length=250, blank=True)
    category = models.ManyToManyField(Category)
    gm = models.BooleanField(verbose_name=_('GM'), help_text=_('Is GM needed for this material?'))
    lendable = models.BooleanField(verbose_name=_('lendable'), default=True,
                                   help_text=_('Should this material be shown for lending?'))
    location = models.ForeignKey(Location, on_delete=models.DO_NOTHING, blank=True, null=True,
                                 help_text=_('Where can this material be found?'))
    rate_class = models.ForeignKey(RateClass, on_delete=models.DO_NOTHING, blank=True, null=True,
                                   help_text=_('What rate class should this material be associated with?'))
    stock = models.CharField(verbose_name=_('stock'), max_length=150, blank=True,
                             help_text=_('How many exemplars are there of this material?'))

    class Meta:
        verbose_name = _('material')
        verbose_name_plural = _('materials')

    def __str__(self):
        return self.name


class MaterialImage(models.Model):
    image = models.ImageField(verbose_name=_('image'))
    material = models.ForeignKey(Material, related_name='images', on_delete=models.DO_NOTHING)

    class Meta:
        verbose_name = _('material image')
        verbose_name_plural = _('material images')


class MaterialAlias(models.Model):
    name = models.CharField(verbose_name=_('name'), max_length=150,
                            help_text=_('Alias for the material, e.g. aliases for "stormbaan" are "Kelly" and '
                                        '"Rambler".'))
    material = models.ForeignKey(Material, on_delete=models.DO_NOTHING)

    class Meta:
        verbose_name = _('material alias')
        verbose_name_plural = _('material aliases')

    def __str__(self):
        return self.name


class Game(models.Model):
    name = models.CharField(max_length=250)
    order = models.PositiveIntegerField(help_text=_('Defines an ordering for the games within a day/part of day'),
                                        editable=False)
    day = models.DateField(help_text=_('On what day are the materials needed?'))
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
        help_text=_('At what part of the day are the materials needed?')
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
    active = models.BooleanField(default=False, help_text=_('Should the event be published?'))
    privileged = models.BooleanField(default=False, help_text=_('Allow only privileged users to change bookings.'))
    locked = models.BooleanField(default=False, help_text=_('Allow no users to change bookings (except admin).'))
    archived = models.BooleanField(default=False, help_text=_('Disable booking.'))
    booking_start = models.DateTimeField(help_text=_('When should the event be opened for booking?'))
    booking_end = models.DateTimeField(help_text=_('When should the event become privileged?'))
    event_start = models.DateField(help_text=_('What is the first day of the event?'))
    event_end = models.DateField(help_text=_('What is the last day of the event?'))

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
