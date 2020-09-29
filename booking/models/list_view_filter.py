import copy

from django.db import models
from django.db.models import Q, Case, When, Value, F, CharField
from django.db.models.functions import Lower
from django.utils.translation import gettext_lazy as _
from adminsortable.models import SortableMixin

from booking.models import Category, Booking


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

    @classmethod
    def create(cls, name, bookings):
        # TODO Maybe create a filterset class that handles running the filters and that
        #  offers a left-over function.
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
        Also sorts the bookings on __str__.

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
        # TODO Just do the sorting in the bookings setter. We need to load the bookings anyway.
        #  The list is also short now.
        # Add names to bookings for sorting
        bookings = bookings.annotate(
            name=Lower(
                Case(
                    When(custom_material__isnull=False, then=F("custom_material")),
                    default=F("material__name"),
                )
            ),
            category=Lower(
                Case(
                    When(custom_material__isnull=False, then=_("Custom material")),
                    When(
                        material__categories__isnull=False,
                        then=F("material__categories__name"),
                    ),
                    default=Value(""),
                    output_field=CharField(),
                )
            ),
        )
        out_set = bookings
        result = []
        for list_view_filter in list_view_filters:
            # Use a copy such that the preloaded filters do not get polluted with
            #  bookings.
            list_view_filter = copy.copy(list_view_filter)
            in_set, out_set = list_view_filter.filter_bookings(out_set)
            list_view_filter._bookings = in_set.order_by("category", "name")
            result.append(list_view_filter)
        result.append(
            ListViewFilter.create(
                _("Common materials"), out_set.order_by("category", "name")
            )
        )

        # Remove the list views that have no bookings
        return [lv for lv in result if len(lv.bookings) > 0]
