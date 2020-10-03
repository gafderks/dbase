from adminsortable.models import SortableMixin
from django.db import models
from django.db.models import Q
from django.utils.translation import gettext_lazy as _

from booking.models import Category


class ListViewFilter(SortableMixin):
    """
    Filter for bookings.
    Filters partition bookings into groups based on the filter attributes.
    When a filter is run, it outputs two sets of bookings, the bookings that belong to
    the group defined by the filter (in-set) and the bookings that do not match the
    attributes of the filter (out-set). The latter bookings are typically used as input
    for other filters to create a pipeline of filters.

    The following filter attributes can be set:
      - included_categories: type Category[]
        in-set:  bookings of materials that have any of their categories in the supplied
                 categories.
        out-set: bookings of materials for which none of its categories matches one of
                 the supplied categories.
      - excluded_categories: type Category[]
        Note: the in-set and out-set are the swapped in-set and out-set for
        included_categories.
        in-set:  bookings of materials for which none of its categories matches one of
                 the supplied categories.
        out-set: bookings of materials that have any of their categories in the supplied
                 categories.
      - gm: type bool
        in-set:  bookings of materials for which the gm attribute matches the supplied
                 boolean value.
        out-set: bookings of materials for which the gm attribute does not match the
                 supplied boolean value.

    If a filter attribute is None or an empty list, its in-set will contain all bookings
    and its out-set will contain no bookings.
    If a category is both in included_categories and in excluded_categories, all
    bookings with this category will be put in the out-set.
    The in-sets for all filter attributes are combined by intersection to create the
    filter's in-set. The out-sets are combined by union. The filter's out-set is the
    complement of its in-set.
    """

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

        :param QuerySet[Booking] bookings: bookings
        :return Tuple[QuerySet[Booking], QuerySet[Booking]]: included and excluded
        bookings
        """
        # Remove custom materials that have no material key
        filters = Q(material__isnull=False)
        if self.gm is not None:
            filters &= Q(material__gm=self.gm)
        if self.included_categories.exists():
            filters &= Q(material__categories__in=self.included_categories.all())
        if self.excluded_categories.exists():
            filters &= ~Q(material__categories__in=self.excluded_categories.all())
        in_set = bookings.filter(filters).distinct()
        out_set = bookings.filter(~filters).distinct()
        return in_set, out_set


class ListView:
    def __init__(self, filters=None):
        """
        Loads ListViewFilters supplied or the default filters
        :param ListViewFilter[] filters: list view filters to use for generating the
         ListView
        """
        if filters is None:
            filters = ListView.DEFAULT_FILTERS
        self.filters = filters

    def _sorted_bookings(self, bookings_queryset):
        """
        Converts a queryset of bookings into a list that gets sorted first on category
        and then on material name.
        :param Booking[] bookings_queryset: bookings
        :return list: sorted list of Booking
        """
        return sorted(
            list(bookings_queryset),
            key=lambda b: (b.display_category.lower(), str(b).lower()),
        )

    def get_lists(self, bookings_queryset):
        """
        Runs the ListViewFilters on the supplied bookings queryset.
        The resulting bookings are sorted on category and material name.
        :param Booking[] bookings_queryset: bookings
        :return List[Tuple[ListViewFilter, List[Booking]]]: list of tuples with list
         view filters and the allocated bookings
        """
        lists = []
        out_set = bookings_queryset
        for _filter in self.filters:
            in_set, out_set = _filter.filter_bookings(out_set)
            bookings = self._sorted_bookings(in_set)
            if len(bookings) > 0:
                lists.append((_filter, bookings))

        if out_set.count() > 0:
            # Append leftover bookings
            lists.append(
                (
                    ListViewFilter(name=_("Common materials")),
                    self._sorted_bookings(out_set),
                )
            )

        return lists


ListView.DEFAULT_FILTERS = ListViewFilter.objects.prefetch_related(
    "included_categories", "excluded_categories"
).filter(enabled=True)
