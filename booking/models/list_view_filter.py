from django.db import models
from django.utils.translation import gettext_lazy as _
from adminsortable.models import SortableMixin

from booking.models import Category


class ListViewFilter(SortableMixin):
    name = models.CharField(verbose_name=_("name"), max_length=150, unique=True)
    description = models.CharField(
        verbose_name=_("description"), max_length=250, blank=True
    )
    enabled = models.BooleanField(verbose_name=_("Enabled"), default=True)
    the_order = models.PositiveIntegerField(
        default=0, editable=False, db_index=True, verbose_name=_("Filter order")
    )

    included_categories = models.ManyToManyField(
        Category, verbose_name=_("included categories"), related_name="+", blank=True
    )
    excluded_categories = models.ManyToManyField(
        Category, verbose_name=_("excluded categories"), related_name="+", blank=True
    )
    gm = models.BooleanField(null=True, verbose_name=_("GM"))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._bookings = []

    class Meta:
        verbose_name = _("list view filter")
        verbose_name_plural = _("list view filters")
        ordering = ["the_order"]

    def __str__(self):
        return self.name

    def filter_materials(self, materials):
        pass

    def filter_bookings(self, bookings):
        """

        :param (list) bookings: bookings
        :return: (tuple) included and excluded bookings
        """
        included_bookings = bookings
        # Remove custom materials that have no material key
        included_bookings = [b for b in included_bookings if b.material is not None]
        if self.gm is not None:
            included_bookings = [
                b for b in included_bookings if b.material.gm == self.gm
            ]
        if self.included_categories.exists():
            included_bookings = [
                b
                for b in included_bookings
                if any(
                    cat in b.material.categories.all()
                    for cat in self.included_categories.all()
                )
            ]
        if self.excluded_categories.exists():
            included_bookings = [
                b
                for b in included_bookings
                if not any(
                    cat in b.material.categories.all()
                    for cat in self.excluded_categories.all()
                )
            ]
        self._bookings = included_bookings
        return (
            included_bookings.sort(key=lambda b: b.material.name),
            [b for b in bookings if b not in included_bookings],
        )

    @classmethod
    def create(cls, name, bookings):
        list_view_filter = cls(name=name)
        list_view_filter.bookings = bookings
        return list_view_filter

    @property
    def bookings(self):
        return self._bookings

    @bookings.setter
    def bookings(self, bookings):
        self._bookings = sorted(
            bookings, key=lambda b: (b.display_category.lower(), str(b).lower())
        )

    @staticmethod
    def get_all_filters(bookings):
        list_view_filters = ListViewFilter.objects.filter(enabled=True)
        result = []
        # We convert to a list since we're gonna use them all anyway
        bookings = list(bookings.all())
        for list_view_filter in list_view_filters:
            included, bookings = list_view_filter.filter_bookings(bookings)
            result.append(list_view_filter)
        result.append(ListViewFilter.create(_("Common materials"), bookings))

        # Remove the list views that have no bookings
        return [lv for lv in result if len(lv.bookings) > 0]
