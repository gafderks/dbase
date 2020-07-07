from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.select import Select

from booking.models import PartOfDay
from .base import wait


def get_part_of_day_name(code):
    return PartOfDay.name_from_code(code)


class GameViewPage(object):
    def __init__(self, test):
        self.test = test

    def add_game(self, day, daypart_code, name, location=""):
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
        # Test if name is in the game
        self.test.wait_for(
            lambda: self.test.assertIn(
                name,
                self.test.browser.find_element_by_css_selector(
                    f'[id="{selected_day}{daypart_code}"]'
                )
                .find_element_by_class_name("game-name")
                .text,
            )
        )

        # Return the id of the newly added game
        return max(
            [
                int(game_elem.get_attribute("data-id"))
                for game_elem in self.test.browser.find_element_by_css_selector(
                    f'[id="{selected_day}{daypart_code}"]'
                ).find_elements_by_css_selector(".card.game")
            ]
        )

    def add_material(self, game_id, amount, material_text, partial_material_text=None):
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
                material_text, material_input.get_attribute("value"),
            )
        )

        # Set the amount
        amount_input = self.test.browser.find_element_by_id(
            f"id_game_booking_amount_{game_id}"
        )
        amount_input.send_keys(amount)

        # Add the material booking
        amount_input.send_keys(Keys.ENTER)

        # Assert that the material is added to the list
        self.test.wait_for(
            lambda: self.test.assertIn(
                material_text,
                self.test.browser.find_element_by_css_selector(f"#game{game_id}")
                .find_element_by_class_name("bookings-table")
                .text,
            )
        )

        # Return the id of the newly added booking
        return max(
            [
                int(booking_elem.get_attribute("data-id"))
                for booking_elem in self.test.browser.find_element_by_css_selector(
                    f"#game{game_id}"
                ).find_elements_by_css_selector(".booking")
            ]
        )
