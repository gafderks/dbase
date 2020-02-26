from datetime import timedelta, datetime, timezone

from django.db import models
from django.utils.translation import gettext_lazy as _


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
        ordering = ["-event_end"]
        permissions = [
            ("can_view_hidden_events", "Can view hidden events"),
            ("can_change_privileged_events", "Can change privileged events"),
            ("can_change_locked_events", "Can change locked events"),
        ]

    def __str__(self):
        return self.name

    @property
    def duration(self):
        return (self.event_end - self.event_start).days

    @property
    def days(self):
        return [
            self.event_start + timedelta(days=day) for day in range(self.duration + 1)
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
    def booking_status_code(self):
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
    def booking_status(self):
        return self.BOOKING_STATUS[self.booking_status_code]

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
