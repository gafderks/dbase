import time

from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from booking.models import PartOfDay
from functional_tests.base import retry_stale


def get_part_of_day_name(code):
    return PartOfDay.name_from_code(code)


class EventViewPage(object):
    def __init__(self, test):
        self.test = test

    def get_catalog_modal(self):
        return self.test.browser.find_element(By.ID, "catalogModal")

    def hover_then_click(self, element_hover, element_click):
        # FireFox does not automatically scroll to the element...
        # @see https://stackoverflow.com/a/52045231
        self.test.scroll_to(element_hover)
        time.sleep(0.5)
        hover_click = (
            ActionChains(self.test.browser)
            .move_to_element(element_hover)
            .move_to_element(element_click)
            .click()
        )
        self.test.wait_for(lambda: hover_click.perform())

    def get_newest_booking_id(self, context=None):
        if context is None:
            context = self.test.browser
        return max(
            [
                int(booking_elem.get_attribute("data-id"))
                for booking_elem in context.find_elements(By.CSS_SELECTOR, "tr.booking")
            ]
        )

    def get_number_of_bookings(self, context=None):
        if context is None:
            context = self.test.browser
        return len(context.find_elements(By.CSS_SELECTOR, "tr.booking"))

    def verify_booking_attributes(self, *args, **kwargs):
        raise NotImplementedError(
            "You need to call verify_booking_attributes on a ListViewPage or a GameViewPage"
        )

    @retry_stale
    def _verify_booking_attributes(self, booking_id, amount, material_text):
        booking = self.test.browser.find_element(
            By.CSS_SELECTOR, f'tr.booking[data-id="{booking_id}"]'
        )

        # Test if material text is correct
        material_text_elem = booking.find_element(By.CSS_SELECTOR, ".booking-name")
        self.test.wait_for(
            lambda: self.test.assertEqual(
                material_text,
                material_text_elem.text,
                "the booking material does not match",
            )
        )

        # Test if the amount is correct
        booking_amount = booking.find_element(By.CLASS_NAME, "booking-amount")
        self.test.wait_for(
            lambda: self.test.assertEqual(
                str(amount), booking_amount.text, "the booking amount does not match"
            )
        )

        # TODO test workweek and comment

    def open_catalog_modal(self, booking_id):
        booking = self.test.browser.find_element(
            By.CSS_SELECTOR, f'tr.booking[data-id="{booking_id}"]'
        )
        material_text_elem = booking.find_element(By.CSS_SELECTOR, ".booking-name")
        material_text_elem.click()

    def edit_booking(self, *args, **kwargs):
        raise NotImplementedError(
            "You need to call edit_booking on a ListViewPage or a GameViewPage"
        )

    def _edit_booking(
        self, booking_id, amount, material_text, partial_material_text=None
    ):
        self.test.check_if_typeahead_loaded()
        # Find the booking on the page
        booking = self.test.browser.find_element(
            By.CSS_SELECTOR, f'.booking[data-id="{booking_id}"]'
        )

        num_bookings_before = self.get_number_of_bookings()

        # If the booking is a duplicate, we need to expand it first
        booking_classes = booking.get_attribute("class").split()
        if "booking-duplicate" in booking_classes and "d-none" in booking_classes:
            # Due to bug cannot click tr, must click td: https://sqa.stackexchange.com/a/34328
            booking.find_element(
                By.XPATH,
                "./preceding-sibling::tr[contains(@class, 'booking-duplicate-handler')]/td[1]",
            ).click()

        booking_name = booking.find_element(By.CSS_SELECTOR, ".booking-name").text

        # Press the edit button
        self.hover_then_click(
            booking,
            booking.find_element(By.CSS_SELECTOR, ".show-md .edit-booking"),
        )

        # Fill in the new details
        # Type the material name
        material_input = self.test.browser.find_element(
            By.ID, f"id_booking_material_{booking_id}"
        )
        for _ in range(len(booking_name)):
            material_input.send_keys(Keys.BACK_SPACE)
        if partial_material_text is not None:
            material_input.send_keys(partial_material_text)
        else:
            material_input.send_keys(material_text)
        material_input.send_keys(Keys.ENTER)

        # As he types, he gets suggestions for materials
        self.test.wait_for(
            lambda: self.test.assertEqual(
                material_text,
                material_input.get_attribute("value"),
                "the material text does not match",
            )
        )

        # Set the amount
        amount_input = self.test.browser.find_element(
            By.ID, f"id_booking_amount_{booking_id}"
        )
        amount_input.clear()
        amount_input.send_keys(amount)

        # Add the material booking
        amount_input.send_keys(Keys.ENTER)

        # Check if there is no more booking with the old details
        self.test.wait_for(
            lambda: self.test.assertEqual(
                self.get_number_of_bookings(),
                num_bookings_before,
                "the number of bookings did not stay equal",
            )
        )

        return booking_id

    def delete_booking(self, booking_id, cancel=False):
        # Find the booking on the page
        booking = self.test.browser.find_element(
            By.CSS_SELECTOR, f'.booking[data-id="{booking_id}"]'
        )
        booking_name = booking.find_element(By.CSS_SELECTOR, ".booking-name").text

        num_bookings_before = self.get_number_of_bookings()

        # Press the delete button
        self.hover_then_click(
            booking,
            booking.find_element(By.CSS_SELECTOR, ".show-md .delete-booking"),
        )

        # Verify the confirmation
        delete_confirmation = self.test.browser.find_element(
            By.ID, "deleteBookingModal"
        )
        self.test.wait_for(
            lambda: self.test.assertTrue(
                booking_name in delete_confirmation.text,
                "the name of the booking should be part of the confirmation message",
            )
        )

        if cancel:
            # Click the cancel button
            self.test.wait_for(
                lambda: delete_confirmation.find_element(
                    By.CSS_SELECTOR, 'button[data-dismiss="modal"]'
                ).click()
            )

            # Check that the modal is hidden now
            self.test.wait_for(
                lambda: self.test.assertFalse(delete_confirmation.is_displayed())
            )

            # Check that no bookings were deleted
            self.test.assertEqual(self.get_number_of_bookings(), num_bookings_before)

        else:  # Confirm deletion
            # Click the confirmation button
            self.test.wait_for(
                lambda: delete_confirmation.find_element(
                    By.CSS_SELECTOR, ".confirm-delete"
                ).click()
            )

            # Check that the modal is hidden now
            self.test.wait_for(
                lambda: self.test.assertFalse(delete_confirmation.is_displayed())
            )

            # Check that one booking was deleted
            self.test.wait_for(
                lambda: self.test.assertEqual(
                    self.get_number_of_bookings(), num_bookings_before - 1
                )
            )

            # Check that the correct booking was deleted
            with self.test.assertRaises(StaleElementReferenceException):
                booking.click()
