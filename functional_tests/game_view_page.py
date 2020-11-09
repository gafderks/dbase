from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.select import Select

from functional_tests.base import retry_stale
from functional_tests.event_view_page import EventViewPage, get_part_of_day_name


class GameViewPage(EventViewPage):
    def get_number_of_games(self, context=None):
        if context is None:
            context = self.test.browser
        return len(context.find_elements_by_css_selector(".card.game"))

    def get_newest_game_id(self, context=None):
        if context is None:
            context = self.test.browser
        return max(
            [
                int(game_elem.get_attribute("data-id"))
                for game_elem in context.find_elements_by_css_selector(".card.game")
            ]
        )

    def verify_booking_attributes(self, booking_id, game_id, amount, material_text):
        # Test booking amount and text
        super()._verify_booking_attributes(booking_id, amount, material_text)

        booking = self.test.browser.find_element_by_css_selector(
            f'tr.booking[data-id="{booking_id}"]'
        )

        # Test if booking is in the correct game
        game_elem = booking.find_element_by_xpath("." + "/.." * 5)  # 5 levels higher
        self.test.wait_for(
            lambda: self.test.assertEqual(
                game_id,
                int(game_elem.get_attribute("data-id")),
                "the booking was not in the correct game",
            )
        )

    def add_game(self, day, daypart_code, name, location=""):
        num_games_before = self.get_number_of_games()
        selected_day = day.strftime("%Y-%m-%d")
        self.test.browser.find_element_by_id(f"id_game_name_{selected_day}").send_keys(
            name
        )
        day_part = Select(
            self.test.browser.find_element_by_id(f"id_game_part_of_day_{selected_day}")
        )
        day_part.select_by_visible_text(get_part_of_day_name(daypart_code))
        self.test.browser.find_element_by_id(
            f"id_game_location_{selected_day}"
        ).send_keys(location)
        self.test.browser.find_element_by_id(
            f"id_game_location_{selected_day}"
        ).send_keys(Keys.ENTER)

        # Wait for the game to be saved and check if there is an additional game now
        self.test.wait_for(
            lambda: self.test.assertEqual(
                self.get_number_of_games(),
                num_games_before + 1,
                "no new game was detected",
            )
        )

        game_id = self.get_newest_game_id(
            context=self.test.browser.find_element_by_css_selector(
                f'[id="{selected_day}{daypart_code}"]'
            )
        )

        self.verify_game_attributes(game_id, day, daypart_code, name, location)

        # Return the id of the newly added game
        return game_id

    @retry_stale
    def verify_game_attributes(self, game_id, day, daypart_code, name, location):
        game_card = self.test.browser.find_element_by_id(f"game{game_id}")
        game_header = game_card.find_element_by_class_name("game-header")

        # Test if the name is in the game
        game_name = game_header.find_element_by_class_name("game-name")
        self.test.wait_for(
            lambda: self.test.assertEqual(
                name, game_name.text, "the game name does not match"
            )
        )

        # Test if the location is in the game
        game_location = game_header.find_element_by_class_name("game-location")
        self.test.wait_for(
            lambda: self.test.assertEqual(
                location, game_location.text, "the game location does not match"
            )
        )

        # Test if game is in the correct daypart
        daypart_elem = game_card.find_element_by_xpath("..")
        daypart_head = daypart_elem.find_element_by_tag_name("h5")
        self.test.wait_for(
            lambda: self.test.assertEqual(
                get_part_of_day_name(daypart_code),
                daypart_head.text,
                "the game is not in the correct part of day",
            )
        )

        # Test if game is in the correct day
        day_elem = daypart_elem.find_element_by_xpath("..")
        day_head = day_elem.find_element_by_tag_name("h4")
        self.test.wait_for(
            lambda: self.test.assertEqual(
                f"day{day.strftime('%Y-%m-%d')}",
                day_head.get_attribute("id"),
                "the game is not in the correct day",
            )
        )

    def add_booking(self, game_id, amount, material_text, partial_material_text=None):
        self.test.check_if_typeahead_loaded()
        # TODO add workweek and comment
        game_card = self.test.browser.find_element_by_id(f"game{game_id}")
        num_bookings_before = self.get_number_of_bookings(context=game_card)

        # Type the material name
        material_input = self.test.browser.find_element_by_id(
            f"id_game_booking_material_{game_id}"
        )
        if partial_material_text is not None:
            material_input.send_keys(partial_material_text)
        else:
            material_input.send_keys(material_text)
        self.test.browser.find_element_by_id(
            f"id_game_booking_material_{game_id}"
        ).send_keys(Keys.ENTER)

        # As he types, he gets suggestions for materials
        self.test.wait_for(
            lambda: self.test.assertEqual(
                material_text,
                material_input.get_attribute("value"),
                "the material text does not match",
            )
        )

        # Set the amount
        amount_input = self.test.browser.find_element_by_id(
            f"id_game_booking_amount_{game_id}"
        )
        amount_input.send_keys(amount)

        # Add the material booking
        amount_input.send_keys(Keys.ENTER)

        # Wait for the booking to be saved and check if there is an additional booking
        # now
        self.test.wait_for(
            lambda: self.test.assertEqual(
                self.get_number_of_bookings(context=game_card),
                num_bookings_before + 1,
                "no new booking was detected",
            )
        )

        booking_id = self.get_newest_booking_id(context=game_card)

        self.verify_booking_attributes(booking_id, game_id, amount, material_text)

        return booking_id

    def edit_game(self, game_id, current_day, daypart_code, name, location=""):
        # Find the game on the page
        game_card = self.test.browser.find_element_by_id(f"game{game_id}")

        num_games_before = self.get_number_of_games()

        # Press the edit button
        self.hover_then_click(
            game_card.find_element_by_css_selector(".game-header"),
            game_card.find_element_by_css_selector(".edit-game"),
        )

        # Fill in the new details
        name_field = self.test.browser.find_element_by_id(f"id_game_name_{game_id}")
        name_field.clear()
        name_field.send_keys(name)
        day_part = Select(
            self.test.browser.find_element_by_id(f"id_game_part_of_day_{game_id}")
        )
        day_part.select_by_visible_text(get_part_of_day_name(daypart_code))
        location_field = self.test.browser.find_element_by_id(
            f"id_game_location_{game_id}"
        )
        location_field.clear()
        location_field.send_keys(location)
        location_field.send_keys(Keys.ENTER)

        self.verify_game_attributes(game_id, current_day, daypart_code, name, location)

        # Check if there is no more game with the old details
        self.test.wait_for(
            lambda: self.test.assertEqual(
                self.get_number_of_games(),
                num_games_before,
                "the number of games did not stay equal",
            )
        )

        return game_id

    def switch_to_list_view(self):
        self.test.browser.find_element_by_class_name("button-listview").click()
        # Wait for the page to switch, after switching the page should have a game view
        #  button to switch back.
        self.test.wait_for(
            lambda: self.test.browser.find_element_by_class_name("button-gameview")
        )

    def delete_booking(self, booking_id, cancel=False):
        # Find the booking on the page
        booking = self.test.browser.find_element_by_css_selector(
            f'.booking[data-id="{booking_id}"]'
        )
        booking_name = booking.find_element_by_css_selector(".booking-name").text

        num_bookings_before = self.get_number_of_bookings()

        # Press the delete button
        self.hover_then_click(
            booking,
            booking.find_element_by_css_selector(".show-md .delete-booking"),
        )

        # Verify the confirmation
        delete_confirmation = self.test.browser.find_element_by_id("deleteBookingModal")
        self.test.wait_for(
            lambda: self.test.assertTrue(
                booking_name in delete_confirmation.text,
                "the name of the booking should be part of the confirmation message",
            )
        )

        if cancel:
            # Click the cancel button
            delete_confirmation.find_element_by_css_selector(
                'button[data-dismiss="modal"]'
            ).click()

            # Check that the modal is hidden now
            self.test.wait_for(
                lambda: self.test.assertFalse(delete_confirmation.is_displayed())
            )

            # Check that no bookings were deleted
            self.test.assertEqual(self.get_number_of_bookings(), num_bookings_before)

        else:  # Confirm deletion
            # Click the confirmation button
            delete_confirmation.find_element_by_css_selector(".confirm-delete").click()

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
