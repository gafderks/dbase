import random

from django.test import TestCase

from booking.models import Booking
from booking.models.list_view_filter import ListView
from booking.tests.factories import BookingFactory, CategoryFactory
from booking.tests.factories.list_view_filter import ListViewFilterFactory


def create_bookings_with_set_of_categories(categories, n=20):
    """
    Creates bookings and assigns their materials randomly to one or more of the
    supplied categories.
    :param int n: number of bookings to create
    :param Category[] categories: categories to assign to the bookings
    :return: Booking[]
    """
    bookings = BookingFactory.create_batch(n)
    for category in categories:
        num = random.randint(0, n)
        for booking in random.sample(bookings, num):
            booking.material.categories.add(category)
    return bookings


def check_sorted_bookings(test, bookings):
    """

    :param TestCase test:
    :param bookings:
    :return:
    """
    bookings = list(bookings)
    # Sorted first on category and then on material name
    sorted_bookings = sorted(
        bookings, key=lambda b: (b.display_category.lower(), str(b).lower())
    )
    test.assertEqual(bookings, sorted_bookings, "bookings are not sorted")


class ListViewFilterModelTest(TestCase):
    # TODO test with custom materials

    def test_include_gm(self):
        _ = BookingFactory.create_batch(20)
        _filter = ListViewFilterFactory(gm=True)
        bookings_qs = Booking.objects.all()
        in_set, out_set = _filter.filter_bookings(bookings_qs)
        self.assertEqual(
            in_set.count() + out_set.count(), 20, "not all bookings are part of output"
        )
        for booking in in_set:
            self.assertEqual(booking.material.gm, True)
        for booking in out_set:
            self.assertEqual(booking.material.gm, False)

    def test_exclude_gm(self):
        _ = BookingFactory.create_batch(20)
        _filter = ListViewFilterFactory(gm=False)
        bookings_qs = Booking.objects.all()
        in_set, out_set = _filter.filter_bookings(bookings_qs)
        self.assertEqual(
            in_set.count() + out_set.count(), 20, "not all bookings are part of output"
        )
        for booking in in_set:
            self.assertEqual(booking.material.gm, False)
        for booking in out_set:
            self.assertEqual(booking.material.gm, True)

    def test_include_category(self):
        categories = CategoryFactory.create_batch(4)
        _ = create_bookings_with_set_of_categories(categories, n=20)
        bookings_qs = Booking.objects.all()
        included_categories = categories[0:2]
        _filter = ListViewFilterFactory(included_categories=included_categories)
        in_set, out_set = _filter.filter_bookings(bookings_qs)
        self.assertEqual(
            in_set.count() + out_set.count(), 20, "not all bookings are part of output"
        )
        for booking in in_set:
            # The bookings in the in_set should have at least one category in common
            #  with included_categories
            self.assertGreaterEqual(
                len(set(booking.material.categories.all()) & set(included_categories)),
                1,
            )
        for booking in out_set:
            # The bookings in the in_set should have no category in common with
            #  included_categories
            self.assertEqual(
                len(set(booking.material.categories.all()) & set(included_categories)),
                0,
            )

    def test_exclude_category(self):
        categories = CategoryFactory.create_batch(4)
        _ = create_bookings_with_set_of_categories(categories, n=20)
        bookings_qs = Booking.objects.all()
        excluded_categories = categories[0:2]
        _filter = ListViewFilterFactory(excluded_categories=excluded_categories)
        in_set, out_set = _filter.filter_bookings(bookings_qs)
        self.assertEqual(
            in_set.count() + out_set.count(), 20, "not all bookings are part of output"
        )
        for booking in in_set:
            # The bookings in the in_set should have no category in common
            #  with included_categories
            self.assertEqual(
                len(set(booking.material.categories.all()) & set(excluded_categories)),
                0,
            )
        for booking in out_set:
            # The bookings in the in_set should have at least one category in common
            #  with included_categories
            self.assertGreaterEqual(
                len(set(booking.material.categories.all()) & set(excluded_categories)),
                1,
            )

    def test_include_and_exclude_same_category(self):
        categories = CategoryFactory.create_batch(2)
        _ = create_bookings_with_set_of_categories(categories, n=20)
        bookings_qs = Booking.objects.all()
        _filter = ListViewFilterFactory(
            included_categories=[categories[0]], excluded_categories=categories
        )
        in_set, out_set = _filter.filter_bookings(bookings_qs)
        self.assertEqual(
            in_set.count() + out_set.count(), 20, "not all bookings are part of output"
        )
        for booking in in_set:
            # categories[0] is both in included and excluded categories we have chosen
            #  to put it in out-set then.
            self.assertNotIn(categories[0], booking.material.categories.all())

    def test_no_filter_attributes(self):
        categories = CategoryFactory.create_batch(2)
        _ = create_bookings_with_set_of_categories(categories, n=20)
        bookings_qs = Booking.objects.all()
        _filter = ListViewFilterFactory(
            included_categories=None, excluded_categories=None, gm=None
        )
        in_set, out_set = _filter.filter_bookings(bookings_qs)
        self.assertEqual(
            in_set.count() + out_set.count(), 20, "not all bookings are part of output"
        )
        # All bookings should be part of in_set
        self.assertEqual(in_set.count(), 20, "not all bookings are part of in_set")

    def test_filters_pipeline(self):
        categories = CategoryFactory.create_batch(4)
        _ = create_bookings_with_set_of_categories(categories, n=30)
        bookings_qs = Booking.objects.all()
        filters = [
            ListViewFilterFactory(included_categories=categories[0:2], gm=False),
            ListViewFilterFactory(included_categories=[categories[3]], gm=True),
        ]
        lists = ListView(filters=filters).get_lists(bookings_qs)
        self.assertEqual(
            sum([len(bookings) for lv, bookings in lists]),
            30,
            "not all bookings are part of output",
        )
        if len(lists) > len(filters):
            left_over_lv, left_over_bookings = lists[-1]
            for booking in left_over_bookings:
                # The bookings are not both gm=false and in category 0 or 1
                self.assertFalse(
                    not booking.material.gm
                    and any(
                        [
                            cat in categories[0:2]
                            for cat in booking.material.categories.all()
                        ]
                    )
                )
                # The bookings are not both gm=false and in category 0 or 1
                self.assertFalse(
                    booking.material.gm
                    and any(
                        [
                            cat == categories[3]
                            for cat in booking.material.categories.all()
                        ]
                    )
                )
        # Check that all lists are sorted
        for lv, bookings in lists:
            check_sorted_bookings(self, bookings)

    def test_include_category_and_descendants(self):
        parent = CategoryFactory()
        child = CategoryFactory(parent=parent)
        categories = [parent, child, *CategoryFactory.create_batch(3)]
        _ = create_bookings_with_set_of_categories(categories, n=20)
        bookings_qs = Booking.objects.all()
        included_categories = [parent, child]
        _filter = ListViewFilterFactory(included_categories=[parent])
        in_set, out_set = _filter.filter_bookings(bookings_qs)
        self.assertEqual(
            in_set.count() + out_set.count(), 20, "not all bookings are part of output"
        )
        for booking in in_set:
            # The bookings in the in_set should have at least one category in common
            #  with included_categories
            self.assertGreaterEqual(
                len(set(booking.material.categories.all()) & set(included_categories)),
                1,
            )
        for booking in out_set:
            # The bookings in the in_set should have no category in common with
            #  included_categories
            self.assertEqual(
                len(set(booking.material.categories.all()) & set(included_categories)),
                0,
            )

    def test_exclude_category_and_descendants(self):
        parent = CategoryFactory()
        child = CategoryFactory(parent=parent)
        categories = [parent, child, *CategoryFactory.create_batch(3)]
        _ = create_bookings_with_set_of_categories(categories, n=20)
        bookings_qs = Booking.objects.all()
        excluded_categories = [parent, child]
        _filter = ListViewFilterFactory(excluded_categories=[parent])
        in_set, out_set = _filter.filter_bookings(bookings_qs)
        self.assertEqual(
            in_set.count() + out_set.count(), 20, "not all bookings are part of output"
        )
        for booking in in_set:
            # The bookings in the in_set should have no category in common
            #  with included_categories
            self.assertEqual(
                len(set(booking.material.categories.all()) & set(excluded_categories)),
                0,
            )
        for booking in out_set:
            # The bookings in the in_set should have at least one category in common
            #  with included_categories
            self.assertGreaterEqual(
                len(set(booking.material.categories.all()) & set(excluded_categories)),
                1,
            )
