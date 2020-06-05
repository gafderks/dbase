import copy

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
        self._bookings = []  # Not to be persisted in db

    class Meta:
        verbose_name = _("list view filter")
        verbose_name_plural = _("list view filters")
        ordering = ["the_order"]

    def __str__(self):
        return self.name

    def filter_bookings(self, bookings):
        """
        Filters the bookings into bookings that satisfy the filters and bookings that do
        not.

        :param QuerySet bookings: bookings
        :return Tuple[list[Booking], list[Booking]]: included and excluded bookings
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
        """
        Creates a ListViewFilter object with bookings preloaded. Used for 'left-over'
        bookings.
        :param str name: name for the ListViewFilter
        :param QuerySet bookings: Bookings to be included
        :return ListViewFilter:
        """
        list_view_filter = cls(name=name)
        list_view_filter.bookings = bookings
        return list_view_filter

    @property
    def bookings(self):
        """
        Returns the bookings in the ListViewFilter.
        :return List[Booking]:
        """
        return self._bookings

    @bookings.setter
    def bookings(self, bookings):
        """
        Setter for bookings. Sorts the bookings first on the name of the category and
        then on the name of the material.
        :param List[Booking] bookings: Bookings to be included
        :return: None
        """
        self._bookings = sorted(
            bookings, key=lambda b: (b.display_category.lower(), str(b).lower())
        )

    @staticmethod
    def run_filters(bookings, list_view_filters=None):
        """
        Returns all ListViewFilter objects with the bookings loaded.

        :param QuerySet bookings: bookings
        :param QuerySet list_view_filters: (optional) preloaded ListViewFilters
        :return List[ListViewFilter]: list of ListViewFilters with the bookings
        allocated
        """
        # TODO cache the ListViewFilter objects into a cached property
        if list_view_filters is None:
            list_view_filters = ListViewFilter.objects.prefetch_related(
                "included_categories", "excluded_categories"
            ).filter(enabled=True)
        result = []
        for list_view_filter in list_view_filters:
            # Use a copy such that the preloaded filters do not get polluted with
            #  bookings.
            list_view_filter = copy.copy(list_view_filter)
            included, bookings = list_view_filter.filter_bookings(bookings)
            result.append(list_view_filter)
        result.append(ListViewFilter.create(_("Common materials"), bookings))

        # Remove the list views that have no bookings
        return [lv for lv in result if len(lv.bookings) > 0]
