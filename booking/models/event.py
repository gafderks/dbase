from datetime import timedelta, datetime, timezone

from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from rules.contrib.models import RulesModel

from booking import rules


class EventManager(models.Manager):
    @staticmethod
    def viewable(user):
        query = Event.objects.all()
        if not user.has_perm("booking.can_view_hidden_events"):
            query = query.filter(visible=True)
        return query

    @staticmethod
    def editable(user):
        query = Event.objects.viewable(user)
        if not user.has_perm("booking.can_book_on_locked_events"):
            query = query.filter(
                locked=False, privileged_booking_end__gt=datetime.now(timezone.utc)
            )
        if not user.has_perm("booking.can_book_on_privileged_events"):
            query = query.filter(booking_end__gt=datetime.now(timezone.utc))
        return query


class Event(RulesModel):
    name = models.CharField(verbose_name=_("name"), max_length=150)
    slug = models.SlugField(null=False, unique=True, help_text=_("URL short name"))
    locked = models.BooleanField(
        verbose_name=_("locked"),
        default=False,
        help_text=_(
            "Manually lock the booking such that users cannot change bookings (except "
            "admin)."
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
        ordering = [
            "-visible",
            "-event_end",
        ]  # first visible events sorted by event_end
        permissions = [
            ("view_hidden_events", "Can view hidden events"),
            ("book_on_privileged_events", "Can book on privileged events"),
            ("book_on_locked_events", "Can book on locked events"),
        ]
        rules_permissions = {
            "view": rules.view_event,
            "book_on": rules.view_event & rules.book_on_event,
        }

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("booking:event_games", kwargs={"event_slug": self.slug})

    @property
    def duration(self):
        return (self.event_end - self.event_start).days

    @property
    def days(self):
        return [
            self.event_start + timedelta(days=day) for day in range(self.duration + 1)
        ]

    class BookingStatus(models.TextChoices):
        HIDDEN = "HI", _("Hidden")
        NOT_STARTED = "NS", _("Not started")
        OPENED = "OP", _("Opened")
        PRIVILEGED = "PR", _("Privileged")
        LOCKED = "LO", _("Locked")

    @property
    def booking_status(self):
        now = datetime.now(timezone.utc)
        if not self.visible:
            return self.BookingStatus.HIDDEN
        if self.locked:
            return self.BookingStatus.LOCKED
        if now < self.booking_start:
            return self.BookingStatus.NOT_STARTED
        if now < self.booking_end:
            return self.BookingStatus.OPENED
        if now < self.privileged_booking_end:
            return self.BookingStatus.PRIVILEGED
        return self.BookingStatus.LOCKED

    @property
    def is_privileged(self):
        """
        Check whether the event is privileged. It is privileged if its locked property
        is False and the booking period has ended and the privileged booking period has
        not ended.
        :return: bool
        """
        return (
            not self.locked
            and self.booking_end
            < datetime.now(timezone.utc)
            < self.privileged_booking_end
        )

    @property
    def is_locked(self):
        """
        Check whether the event is locked. It is locked if either its locked property is
        True or the privileged booking period has ended.
        :return: bool
        """
        return self.locked or datetime.now(timezone.utc) > self.privileged_booking_end
