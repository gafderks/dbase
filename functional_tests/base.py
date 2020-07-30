from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.test import override_settings
from selenium import webdriver
from selenium.common.exceptions import (
    WebDriverException,
    StaleElementReferenceException,
)
import time
from django.conf import settings

from .management.commands.create_session import create_pre_authenticated_session

MAX_WAIT = 10


def wait(fn):
    def modified_fn(*args, **kwargs):
        start_time = time.time()
        while True:
            try:
                return fn(*args, **kwargs)
            except (AssertionError, WebDriverException) as e:
                if time.time() - start_time > MAX_WAIT:
                    raise e
                time.sleep(0.5)

    return modified_fn


def retry_stale(fn):
    def modified_fn(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except StaleElementReferenceException:
            return fn(*args, **kwargs)

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

    @retry_stale
    def retry_on_stale(self, fn):
        return fn()

    @wait
    def wait_to_be_logged_in(self, user_label):
        self.browser.find_element_by_css_selector('[href="/users/logout/"]')
        navbar = self.browser.find_element_by_css_selector(".navbar")
        self.assertIn(user_label, navbar.get_attribute("innerHTML"))

    @wait
    def wait_to_be_logged_out(self, email):
        self.browser.find_element_by_name("email")
        navbar = self.browser.find_element_by_css_selector(".navbar")
        self.assertNotIn(email, navbar.text)

    def create_pre_authenticated_session(self, user):
        """
        :param User user:
        :return:
        """
        session_key = create_pre_authenticated_session(user)
        # To set a cookie we need to first visit the domain.
        # Use the homepage as a non-existing page seems to break CSRF cookie
        self.browser.get(self.live_server_url)
        self.browser.add_cookie(
            dict(
                name=settings.SESSION_COOKIE_NAME,
                value=session_key,
                path="/",
                secure=False,
            )
        )
        self.browser.refresh()
