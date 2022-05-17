import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from tests.functional_tests.home.test_home_base_helper import \
    TestHelperNoStatic

from home.tests.test_home_helper import HomeHelperMixin

# QUANDO FOR ELABORAR OS TESTES, OLHAR NO GITHUB DO PROJETO
# AS TÉCNICAS UTILIZADAS, REESCREVER ESTES TESTES E CRIAR NOVOS


@pytest.mark.selenium
class TestHomeIndexPage(TestHelperNoStatic, HomeHelperMixin):
    """
    These tests are being created based on LiveServerTestCase
    That is, without CSS or JS files
    """
    # Testing user trying to login with a nonexistent user
    # the return should be a error message
    def test_home_index_login_nonexistent_user(self):
        # User opens browser
        self.browser.get(self.live_server_url)

        # User finds an input field related to the email and click on it
        email_input = self.browser.find_element(by=By.ID, value='use_login')
        email_input.click()

        # User types e-mail on it
        email_input.send_keys('jane.doe@email.com')

        # User finds an input field related to the password and click on it
        pass_input = self.browser.find_element(by=By.ID, value='use_password')
        pass_input.click()

        # User types password on it
        pass_input.send_keys('$Trong1234')

        # User finds login button and click on it
        login_button = self.browser.find_element(
            by=By.XPATH, value='//button[@type="submit"]'
        )
        login_button.click()

        # An error message will display
        body = self.browser.find_element(by=By.TAG_NAME, value='body')
        self.assertIn('Incorrect email or password.', body.text)

    # Testing user trying to login with a irregular email
    def test_home_index_login_irregular_email(self):
        # User opens browser
        self.browser.get(self.live_server_url)

        # User finds an input field related to the email and click on it
        email_input = self.browser.find_element(by=By.ID, value='use_login')
        email_input.click()

        # User types irregular e-mail on it
        email_input.send_keys('jane.doe@email')

        # User finds an input field related to the password and click on it
        pass_input = self.browser.find_element(by=By.ID, value='use_password')
        pass_input.click()

        # User types password on it and click ENTER
        pass_input.send_keys('$Trong1234')
        pass_input.send_keys(Keys.ENTER)

        # An error message will display
        body = self.browser.find_element(by=By.TAG_NAME, value='body')
        self.assertIn('Invalid email or password.', body.text)

    # Testing user login in with a existing email of a validated user
    def test_home_index_login_in_existing_email_validated_user(self):
        # Creating a user
        self.make_user(use_is_valid=True)

        # User opens browser
        self.browser.get(self.live_server_url)

        # User finds an input field related to the email and click on it
        email_input = self.browser.find_element(by=By.ID, value='use_login')
        email_input.click()

        # User types e-mail on it
        email_input.send_keys('jane.doe@email.com')

        # User finds an input field related to the password and click on it
        pass_input = self.browser.find_element(by=By.ID, value='use_password')
        pass_input.click()

        # User types password on it and click ENTER
        pass_input.send_keys('$Trong1234')
        pass_input.send_keys(Keys.ENTER)

        # An successful message will display (WILL FAIL IN THE NEAR FUTURE)
        body = self.browser.find_element(by=By.TAG_NAME, value='body')
        self.assertIn('You are logged in.', body.text)
