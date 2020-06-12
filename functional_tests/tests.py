from django.test import LiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time


class EventBookingTest(LiveServerTestCase):
    def setUp(self):
        self.browser = webdriver.Firefox()

    def tearDown(self):
        self.browser.quit()

    def test_can_create_booking_and_retrieve_it_later(self):
        # Bob visits the DBase to book materials for next event
        self.browser.get(self.live_server_url)

        # He gets redirected to the login page
        self.fail("Finish the test!")
        # He types his credentials and logs into the DBase

        # Bob may book on the event

        # The page shows the group that Bob belongs to his group

        # He adds a game to the Thursday

        # He notes that the game is added to the page

        # On the game he adds a booking for a material

        # As he types, he gets suggestions for materials

        # Bob decides to add another game

        # Bob changes the order of the games
