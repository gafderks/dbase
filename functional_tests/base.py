from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.test import override_settings
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.keys import Keys
import time

MAX_WAIT = 10


def wait(fn):
    def modified_fn(*args, **kwargs):
        print("run wait")
        start_time = time.time()
        while True:
            try:
                return fn(*args, **kwargs)
            except (AssertionError, WebDriverException) as e:
                if time.time() - start_time > MAX_WAIT:
                    raise e
                time.sleep(0.5)

    return modified_fn


english = override_settings(LANGUAGE_CODE="en-US", LANGUAGES=(("en", "English"),),)


@override_settings(
    STATICFILES_STORAGE="django.contrib.staticfiles.storage.StaticFilesStorage",
    DEBUG=True,
)
class FunctionalTest(StaticLiveServerTestCase):
    def setUp(self):
        self.browser = webdriver.Firefox()

    def tearDown(self):
        self.browser.quit()

    @wait
    def wait_for(self, fn):
        return fn()

    # @wait
    # def wait_for_row_in_list_table(self, row_text):
    #     table = self.browser.find_element_by_id("id_list_table")
    #     rows = table.find_elements_by_tag_name("tr")
    #     self.assertIn(row_text, [row.text for row in rows])
    #
    # def get_item_input_box(self):
    #     return self.browser.find_element_by_id("id_text")
    #
    # def add_list_item(self, item_text):
    #     num_rows = len(self.browser.find_elements_by_css_selector("#id_list_table tr"))
    #     self.get_item_input_box().send_keys(item_text)
    #     self.get_item_input_box().send_keys(Keys.ENTER)
    #     item_number = num_rows + 1
    #     self.wait_for_row_in_list_table(f"{item_number}: {item_text}")

    @wait
    def wait_to_be_logged_in(self, user_label):
        print(self.browser.page_source)
        self.browser.find_element_by_link_text("Logout")
        navbar = self.browser.find_element_by_css_selector(".navbar")
        self.assertIn(user_label, navbar.text)

    @wait
    def wait_to_be_logged_out(self, email):
        self.browser.find_element_by_name("email")
        navbar = self.browser.find_element_by_css_selector(".navbar")
        self.assertNotIn(email, navbar.text)
