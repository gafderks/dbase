from functional_tests.event_view_page import EventViewPage, get_part_of_day_name


class ListViewPage(EventViewPage):
    def switch_to_game_view(self):
        self.test.wait_for(
            lambda: self.test.browser.find_element_by_class_name(
                "button-gameview"
            ).click()
        )
        # Wait for the page to switch, after switching the page should have a list view
        #  button to switch back.
        self.test.wait_for(
            lambda: self.test.browser.find_element_by_class_name("button-listview")
        )

    def verify_booking_attributes(
        self, booking_id, amount, material_text, day, daypart_code, game_name
    ):
        # Test booking amount and text
        super()._verify_booking_attributes(booking_id, amount, material_text)

        booking = self.test.browser.find_element_by_css_selector(
            f'tr.booking[data-id="{booking_id}"]'
        )

        # Test if the name of the game is in the booking
        game_name_elem = booking.find_element_by_class_name("booking-game")
        self.test.wait_for(
            lambda: self.test.assertEqual(
                game_name, game_name_elem.text, "the game name does not match"
            )
        )

        # Test if booking is in the correct daypart
        daypart_elem = booking.find_element_by_xpath("." + "/.." * 6)  # 6 levels higher
        daypart_head = daypart_elem.find_element_by_tag_name("h5")
        self.test.wait_for(
            lambda: self.test.assertEqual(
                get_part_of_day_name(daypart_code),
                daypart_head.text,
                "the booking is not in the correct part of day",
            )
        )

        # Test if booking is in the correct day
        day_elem = daypart_elem.find_element_by_xpath("..")
        day_head = day_elem.find_element_by_tag_name("h4")
        self.test.wait_for(
            lambda: self.test.assertEqual(
                f"day{day.strftime('%Y-%m-%d')}",
                day_head.get_attribute("id"),
                "the booking is not in the correct day",
            )
        )

    def edit_booking(
        self,
        booking_id,
        amount,
        material_text,
        day,
        daypart_code,
        game_name,
        partial_material_text=None,
    ):
        super()._edit_booking(booking_id, amount, material_text, partial_material_text)
        self.verify_booking_attributes(
            booking_id, amount, material_text, day, daypart_code, game_name
        )
