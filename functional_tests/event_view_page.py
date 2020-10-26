from selenium.webdriver import ActionChains

from booking.models import PartOfDay
from functional_tests.base import wait, retry_stale


def get_part_of_day_name(code):
    return PartOfDay.name_from_code(code)


class EventViewPage(object):
    def __init__(self, test):
        self.test = test

    def get_catalog_modal(self):
        return self.test.browser.find_element_by_id("catalogModal")

    def hover_then_click(self, element_hover, element_click):
        hover_click = (
            ActionChains(self.test.browser)
            .move_to_element(element_hover)
            .move_to_element(element_click)
        )
        hover_click.click().perform()

    def get_newest_booking_id(self, context=None):
        if context is None:
            context = self.test.browser
        return max(
            [
                int(booking_elem.get_attribute("data-id"))
                for booking_elem in context.find_elements_by_css_selector("tr.booking")
            ]
        )

    def get_number_of_bookings(self, context=None):
        if context is None:
            context = self.test.browser
        return len(context.find_elements_by_css_selector("tr.booking"))

    @retry_stale
    def _verify_booking_attributes(self, booking_id, amount, material_text):
        booking = self.test.browser.find_element_by_css_selector(
            f'tr.booking[data-id="{booking_id}"]'
        )

        # Test if material text is correct
        material_text_elem = booking.find_element_by_css_selector(".booking-name")
        self.test.wait_for(
            lambda: self.test.assertEqual(
                material_text,
                material_text_elem.text,
                "the booking material does not match",
            )
        )

        # Test if the amount is correct
        booking_amount = booking.find_element_by_class_name("booking-amount")
        self.test.wait_for(
            lambda: self.test.assertEqual(
                str(amount), booking_amount.text, "the booking amount does not match"
            )
        )

        # TODO test workweek and comment

    def open_catalog_modal(self, booking_id):
        booking = self.test.browser.find_element_by_css_selector(
            f'tr.booking[data-id="{booking_id}"]'
        )
        material_text_elem = booking.find_element_by_css_selector(".booking-name")
        material_text_elem.click()
