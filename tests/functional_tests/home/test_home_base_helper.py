import time

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.test import LiveServerTestCase
from library.utils.browser import make_chrome_browser


class TestBase:
    def sleep(self, sec=5):
        return time.sleep(sec)


class TestHelperNoStatic(LiveServerTestCase, TestBase):
    def setUp(self) -> None:
        self.browser = make_chrome_browser()
        return super().setUp()

    def tearDown(self) -> None:
        self.browser.quit()
        return super().tearDown()


class TestHelperStatic(StaticLiveServerTestCase, TestBase):
    def setUp(self) -> None:
        self.browser = make_chrome_browser()
        return super().setUp()

    def tearDown(self) -> None:
        self.browser.quit()
        return super().tearDown()
