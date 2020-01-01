from django.contrib.auth import get_user_model
from django.db import models
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from datetime import timedelta, datetime, timezone
from djmoney.models.fields import MoneyField
from djmoney.models.validators import MinMoneyValidator

from users.models import Group


class Category(models.Model):
    name = models.CharField(verbose_name=_("name"), max_length=150, unique=True)
    description = models.CharField(
        verbose_name=_("description"), max_length=250, blank=True
    )

    class Meta:
        verbose_name = _("category")
        verbose_name_plural = _("categories")

    def __str__(self):
        return self.name


class RateClass(models.Model):
    name = models.CharField(verbose_name=_("name"), max_length=150, unique=True)
    description = models.CharField(
        verbose_name=_("description"), max_length=250, blank=True
    )
    rate = MoneyField(
        verbose_name=_("rate"),
        decimal_places=2,
        max_digits=6,
        default_currency="EUR",
        validators=[MinMoneyValidator(0)],
    )

    class Meta:
        verbose_name = _("rate class")
        verbose_name_plural = _("rate classes")

    def __str__(self):
        return self.name


class Location(models.Model):
    name = models.CharField(verbose_name=_("name"), max_length=150, unique=True)

    class Meta:
        verbose_name = _("location")
        verbose_name_plural = _("locations")

    def __str__(self):
        return self.name


class Material(models.Model):
    name = models.CharField(verbose_name=_("name"), max_length=150, unique=True)
    description = models.CharField(
        verbose_name=_("description"), max_length=250, blank=True
    )
    categories = models.ManyToManyField(Category, related_name="materials")
    gm = models.BooleanField(
        verbose_name=_("GM"), help_text=_("Is GM needed for this material?")
    )
    lendable = models.BooleanField(
        verbose_name=_("lendable"),
        default=True,
        help_text=_("Should this material be shown for lending?"),
    )
    location = models.ForeignKey(
        Location,
        on_delete=models.DO_NOTHING,
        blank=True,
        null=True,
        verbose_name=_("location"),
        help_text=_("Where can this material be found?"),
        related_name="materials",
    )
    rate_class = models.ForeignKey(
        RateClass,
        on_delete=models.DO_NOTHING,
        blank=True,
        null=True,
        verbose_name=_("rate class"),
        help_text=_("What rate class should this material be associated with?"),
    )
    stock = models.CharField(
        verbose_name=_("stock"),
        max_length=150,
        blank=True,
        help_text=_("How many exemplars are there of this material?"),
    )

    class Meta:
        verbose_name = _("material")
        verbose_name_plural = _("materials")

    def __str__(self):
        return self.name


class MaterialImage(models.Model):
    image = models.ImageField(upload_to="materials", verbose_name=_("image"))
    material = models.ForeignKey(
        Material,
        related_name="images",
        on_delete=models.DO_NOTHING,
        verbose_name=_("material"),
    )

    def image_tag(self):
        return mark_safe(
            '<img src="{}" width="150" height="150" />'.format(self.image.url)
        )

    image_tag.short_description = "Preview"

    class Meta:
        verbose_name = _("material image")
        verbose_name_plural = _("material images")


class MaterialAlias(models.Model):
    name = models.CharField(
        verbose_name=_("name"),
        max_length=150,
        unique=True,
        help_text=_(
            'Alias for the material, e.g. aliases for "stormbaan" are "Kelly" and '
            '"Rambler".'
        ),
    )
    material = models.ForeignKey(
        Material, on_delete=models.DO_NOTHING, verbose_name=_("material")
    )

    class Meta:
        verbose_name = _("material alias")
        verbose_name_plural = _("material aliases")

    def __str__(self):
        return self.name


class Game(models.Model):
    creator = models.ForeignKey(
        get_user_model(), on_delete=models.DO_NOTHING, verbose_name=_("creator")
    )
    name = models.CharField(verbose_name=_("name"), max_length=250)
    order = models.PositiveIntegerField(
        verbose_name=_("order"),
        help_text=_("Defines an ordering for the games within a day/part of day"),
        editable=False,
    )
    day = models.DateField(
        verbose_name=_("day"), help_text=_("On what day are the materials needed?")
    )
    MORNING = "MO"
    AFTERNOON = "AF"
    EVENING = "EV"
    DAY = "DA"
    NIGHT = "NI"
    PART_OF_DAY_CHOICES = [
        (MORNING, _("Morning")),
        (AFTERNOON, _("Afternoon")),
        (EVENING, _("Evening")),
        (NIGHT, _("Night")),
        (DAY, _("Day")),
    ]
    part_of_day = models.CharField(
        verbose_name=_("part of day"),
        max_length=2,
        choices=PART_OF_DAY_CHOICES,
        default=MORNING,
        help_text=_("At what part of the day are the materials needed?"),
    )

    class Meta:
        verbose_name = _("game")
        verbose_name_plural = _("games")

    def __str__(self):
        return self.name


class EventManager(models.Manager):
    def for_user(self, user):
        query = Event.objects.all()
        if not user.has_perm("booking.can_view_hidden_events"):
            query = query.filter(visible=True)
        return query


class Event(models.Model):
    name = models.CharField(verbose_name=_("name"), max_length=150)
    locked = models.BooleanField(
        verbose_name=_("locked"),
        default=False,
        help_text=_(
            "Manually lock the booking such that users cannot change bookings (except admin)."
        ),
    )
    visible = models.BooleanField(
        verbose_name=_("visible"),
        default=True,
        help_text=_("Should the event be visible?"),
    )
    booking_start = models.DateTimeField(
        verbose_name=_("start date booking period"),
        help_text=_("When should the event be opened for booking?"),
    )
    booking_end = models.DateTimeField(
        verbose_name=_("end date booking period"),
        help_text=_("When should the event become privileged?"),
    )
    privileged_booking_end = models.DateTimeField(
        verbose_name=_("end date privileged booking period"),
        help_text=_("When should the event become locked?"),
    )
    event_start = models.DateField(
        verbose_name=_("event start date"),
        help_text=_("What is the first day of the event?"),
    )
    event_end = models.DateField(
        verbose_name=_("event end date"),
        help_text=_("What is the last day of the event?"),
    )

    objects = EventManager()

    class Meta:
        verbose_name = _("event")
        verbose_name_plural = _("events")
        get_latest_by = "event_end"
        ordering = ["-event_end"]
        permissions = [
            ("can_view_hidden_events", "Can view hidden events"),
            ("can_change_privileged_events", "Can change privileged events"),
            ("can_change_locked_events", "Can change locked events"),
        ]

    def __str__(self):
        return self.name

    def duration(self):
        return (self.event_end - self.event_start).days

    def days(self):
        return [
            self.event_start + timedelta(days=day) for day in range(self.duration() + 1)
        ]

    HIDDEN = "HI"
    NOT_STARTED = "NS"
    OPENED = "OP"
    PRIVILEGED = "PR"
    LOCKED = "LO"
    BOOKING_STATUS = {
        HIDDEN: _("Hidden"),
        NOT_STARTED: _("Not started"),
        OPENED: _("Opened"),
        PRIVILEGED: _("Privileged"),
        LOCKED: _("Locked"),
    }

    @property
    def booking_status(self):
        now = datetime.now(timezone.utc)
        if not self.visible:
            return self.HIDDEN
        if self.locked:
            return self.LOCKED
        if now < self.booking_start:
            return self.NOT_STARTED
        if now < self.booking_end:
            return self.OPENED
        if now < self.privileged_booking_end:
            return self.PRIVILEGED
        return self.LOCKED

    @property
    def is_privileged(self):
        return (
            self.booking_end < datetime.now(timezone.utc) < self.privileged_booking_end
            and not self.locked
        )

    @property
    def is_locked(self):
        return self.locked or datetime.now(timezone.utc) > self.privileged_booking_end

    def user_may_edit(self, user):
        if not self.visible and not user.has_perm("booking.can_view_hidden_events"):
            return False
        if self.is_locked and not user.has_perm("booking.can_change_locked_events"):
            return False
        if self.is_privileged and not user.has_perm(
            "booking.can_change_privileged_events"
        ):
            return False
        return True


class Booking(models.Model):
    requester = models.ForeignKey(
        get_user_model(), on_delete=models.DO_NOTHING, verbose_name=_("requester")
    )
    group = models.ForeignKey(
        Group, on_delete=models.DO_NOTHING, verbose_name=_("group")
    )
    day = models.DateField(
        verbose_name=_("day"), help_text=_("On what day are the materials needed?")
    )
    MORNING = "MO"
    AFTERNOON = "AF"
    EVENING = "EV"
    DAY = "DA"
    NIGHT = "NI"
    PART_OF_DAY_CHOICES = [
        (MORNING, _("Morning")),
        (AFTERNOON, _("Afternoon")),
        (EVENING, _("Evening")),
        (NIGHT, _("Night")),
        (DAY, _("Day")),
    ]
    part_of_day = models.CharField(
        verbose_name=_("part of day"),
        max_length=2,
        choices=PART_OF_DAY_CHOICES,
        default=MORNING,
        help_text=_("At what part of the day are the materials needed?"),
    )
    game = models.ForeignKey(
        Game, on_delete=models.DO_NOTHING, null=True, verbose_name=_("game")
    )
    material = models.ForeignKey(
        Material, on_delete=models.DO_NOTHING, verbose_name=_("material")
    )
    workweek = models.CharField(
        max_length=150, blank=True, null=True, verbose_name=_("workweek")
    )
    comment = models.CharField(
        max_length=250, blank=True, null=True, verbose_name=_("comment")
    )
    amount = models.CharField(max_length=150, verbose_name=_("amount"))
    event = models.ForeignKey(Event, on_delete=models.CASCADE, verbose_name=_("event"))

    class Meta:
        verbose_name = _("booking")
        verbose_name_plural = _("bookings")
        permissions = [
            ("can_change_other_groups_bookings", "Can change bookings of other groups"),
            ("can_view_others_groups_bookings", "Can view bookings of other groups"),
        ]

    def __str__(self):
        return self.material.name
