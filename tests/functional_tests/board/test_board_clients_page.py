import pytest
from home.models import User
from home.tests.test_home_helper import HomeHelperMixin
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from tests.functional_tests.home.test_home_base_helper import TestHelperStatic

from board.models import Country, State
from board.tests.test_board_helper import BoardHelperMixin


@pytest.mark.selenium
class TestBoardClientsPage(TestHelperStatic, HomeHelperMixin,
                           BoardHelperMixin):
    """
    These tests are being created based on StaticLiveServerTestCase
    That is, with CSS and JS files
    """
    def setUp(self) -> None:
        self.user = self.make_user(use_is_valid=True)
        self.country = self.make_country()
        self.state = self.make_state(
            country=Country.objects.get(id=self.country.id)
        )
        self.make_client(
            user=User.objects.get(id=self.user.id),
            country=Country.objects.get(id=self.country.id),
            state=State.objects.get(id=self.state.id),
            cli_email='mail@email.com',
            cli_phone='1234567890',
            cli_responsible='Responsible'
        )
        return super().setUp()

    def _test_path(self):
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

        # User finds sidebar labels and click on it
        sidebar_labels = self.browser.find_element(
            by=By.XPATH, value='//span[@key="t-labels"]'
        )
        sidebar_labels.click()

        # User finds sidebar clients and click on it
        sidebar_clients = self.browser.find_element(
            by=By.XPATH, value='//a[@key="t-clients"]'
        )
        self.sleep(1)
        sidebar_clients.click()

    # Testing user login in with a existing email of a validated user
    # going to clients view details
    def test_board_clients_login_in_view_details(self):
        # Initialiazing test
        self._test_path()

        # User finds view details and click on it
        view = self.browser.find_element(
            by=By.XPATH, value='//button[@data-bs-target=".labelDetailsModal"]'
        )
        view.click()
        self.sleep(1)

        # A view description will display and user will check Client
        modal = self.browser.find_element(
            by=By.XPATH,
            value='//p[@class="mb-4 modal_client"]/span'
        )
        self.assertIn('Client', modal.text)

        # Than check State
        modal = self.browser.find_element(
            by=By.XPATH,
            value='//p[@class="mb-2 modal_state"]/span'
        )
        self.assertIn('State', modal.text)

        # Than check Country
        modal = self.browser.find_element(
            by=By.XPATH,
            value='//p[@class="mb-2 modal_region"]/span'
        )
        self.assertIn('Country', modal.text)

        # Than check City
        modal = self.browser.find_element(
            by=By.XPATH,
            value='//p[@class="mb-4 modal_city"]/span'
        )
        self.assertIn('City', modal.text)

        # Than check E-mail
        modal = self.browser.find_element(
            by=By.XPATH,
            value='//p[@class="mb-2 modal_email"]/span'
        )
        self.assertIn('mail@email.com', modal.text)

        # Than check Phone
        modal = self.browser.find_element(
            by=By.XPATH,
            value='//p[@class="mb-2 modal_phone"]/span'
        )
        self.assertIn('1234567890', modal.text)

        # Than check Responsible
        modal = self.browser.find_element(
            by=By.XPATH,
            value='//p[@class="mb-2 modal_responsible"]/span'
        )
        self.assertIn('Responsible', modal.text)

    # going to clients edit label - same data
    def test_board_clients_login_in_edit_label_same_data(self):
        # Initialiazing test
        self._test_path()

        # User finds edit icon and click on it
        edit = self.browser.find_element(
            by=By.XPATH, value='//a[@data-bs-target=".labelEditModal"]'
        )
        edit.click()
        self.sleep(1)

        # User finds button and click on it
        button = self.browser.find_element(
            by=By.XPATH,
            value='//div[@id="labelEditModal"]/div/div/form/div/button'
        )
        button.click()

        # A success message will display
        body = self.browser.find_element(by=By.TAG_NAME, value='body')
        self.assertIn(
            'Client edited successfully.',
            body.text
        )

    # going to clients edit label - update duplicated client name
    def test_board_clients_login_in_edit_label_duplicated_client_name(self):
        self.make_client(
            user=User.objects.get(id=self.user.id),
            cli_name='Second Client',
            cli_slug='newslug',
            country=Country.objects.get(id=self.country.id),
            state=State.objects.get(id=self.state.id),
            cli_email='mail1@email.com',
            cli_phone='1234567890',
            cli_responsible='Responsible'
        )

        # Initialiazing test
        self._test_path()

        # User finds edit icon and click on it
        edit = self.browser.find_element(
            by=By.XPATH, value='//a[@data-bs-target=".labelEditModal"]'
        )
        edit.click()
        self.sleep(1)

        client = self.browser.find_element(
            by=By.XPATH,
            value='//input[@id="client"]'
        )
        client.click()

        # User writes on input
        client.clear()
        client.send_keys('Second Client')

        # User finds button and click on it
        button = self.browser.find_element(
            by=By.XPATH,
            value='//div[@id="labelEditModal"]/div/div/form/div/button'
        )
        button.click()

        # An error message will display
        body = self.browser.find_element(by=By.TAG_NAME, value='body')
        self.assertIn(
            'This client is already register in our database and cannot be used.',  # noqa: E501
            body.text
        )

    # going to clients edit label - update empty client name
    def test_board_clients_login_in_edit_label_empty_client_name(self):
        # Initialiazing test
        self._test_path()

        # User finds edit icon and click on it
        edit = self.browser.find_element(
            by=By.XPATH, value='//a[@data-bs-target=".labelEditModal"]'
        )
        edit.click()
        self.sleep(1)

        client = self.browser.find_element(
            by=By.XPATH,
            value='//input[@id="client"]'
        )
        client.click()

        # User clear input
        client.clear()

        # User finds button and click on it
        button = self.browser.find_element(
            by=By.XPATH,
            value='//div[@id="labelEditModal"]/div/div/form/div/button'
        )
        button.click()

        # An error message will display
        modal = self.browser.find_element(
            by=By.XPATH,
            value='//div[@id="labelEditModal"]'
        )
        self.assertIn("Please enter your client's name", modal.text)

    # going to clients edit label - update bad client name
    def test_board_clients_login_in_edit_label_bad_client_name(self):
        # Initialiazing test
        self._test_path()

        # User finds edit icon and click on it
        edit = self.browser.find_element(
            by=By.XPATH, value='//a[@data-bs-target=".labelEditModal"]'
        )
        edit.click()
        self.sleep(1)

        client = self.browser.find_element(
            by=By.XPATH,
            value='//input[@id="client"]'
        )
        client.click()

        # User writes on input
        client.send_keys('Nada;')

        # User finds button and click on it
        button = self.browser.find_element(
            by=By.XPATH,
            value='//div[@id="labelEditModal"]/div/div/form/div/button'
        )
        button.click()

        # An error message will display
        modal = self.browser.find_element(
            by=By.XPATH,
            value='//div[@id="labelEditModal"]'
        )
        self.assertIn(
            'Entry cannot contain disallowed characters. e.g. ";"', modal.text
        )

    # going to clients edit label - update valid client name
    def test_board_clients_login_in_edit_label_valid_client_name(self):
        # Initialiazing test
        self._test_path()

        # User finds edit icon and click on it
        edit = self.browser.find_element(
            by=By.XPATH, value='//a[@data-bs-target=".labelEditModal"]'
        )
        edit.click()
        self.sleep(1)

        client = self.browser.find_element(
            by=By.XPATH,
            value='//input[@id="client"]'
        )
        client.click()

        # User writes on input
        client.send_keys('Nada')

        # User finds button and click on it
        button = self.browser.find_element(
            by=By.XPATH,
            value='//div[@id="labelEditModal"]/div/div/form/div/button'
        )
        button.click()

        # A success message will display
        body = self.browser.find_element(by=By.TAG_NAME, value='body')
        self.assertIn(
            'Client edited successfully.',
            body.text
        )

    # going to clients edit label - update empty city
    def test_board_clients_login_in_edit_label_empty_city(self):
        # Initialiazing test
        self._test_path()

        # User finds edit icon and click on it
        edit = self.browser.find_element(
            by=By.XPATH, value='//a[@data-bs-target=".labelEditModal"]'
        )
        edit.click()
        self.sleep(1)

        city = self.browser.find_element(
            by=By.XPATH,
            value='//input[@id="city"]'
        )
        city.click()

        # User clear input
        city.clear()

        # User finds button and click on it
        button = self.browser.find_element(
            by=By.XPATH,
            value='//div[@id="labelEditModal"]/div/div/form/div/button'
        )
        button.click()

        # An error message will display
        modal = self.browser.find_element(
            by=By.XPATH,
            value='//div[@id="labelEditModal"]'
        )
        self.assertIn("Please enter your client's city of origin", modal.text)

    # going to clients edit label - update bad city data
    def test_board_clients_login_in_edit_label_bad_city(self):
        # Initialiazing test
        self._test_path()

        # User finds edit icon and click on it
        edit = self.browser.find_element(
            by=By.XPATH, value='//a[@data-bs-target=".labelEditModal"]'
        )
        edit.click()
        self.sleep(1)

        city = self.browser.find_element(
            by=By.XPATH,
            value='//input[@id="city"]'
        )
        city.click()

        # User writes on input
        city.send_keys('Nada;')

        # User finds button and click on it
        button = self.browser.find_element(
            by=By.XPATH,
            value='//div[@id="labelEditModal"]/div/div/form/div/button'
        )
        button.click()

        # An error message will display
        modal = self.browser.find_element(
            by=By.XPATH,
            value='//div[@id="labelEditModal"]'
        )
        self.assertIn(
            'Entry cannot contain disallowed characters. e.g. ";"', modal.text
        )

    # going to clients edit label - update valid city
    def test_board_clients_login_in_edit_label_valid_city(self):
        # Initialiazing test
        self._test_path()

        # User finds edit icon and click on it
        edit = self.browser.find_element(
            by=By.XPATH, value='//a[@data-bs-target=".labelEditModal"]'
        )
        edit.click()
        self.sleep(1)

        city = self.browser.find_element(
            by=By.XPATH,
            value='//input[@id="city"]'
        )
        city.click()

        # User writes on input
        city.send_keys('Nada')

        # User finds button and click on it
        button = self.browser.find_element(
            by=By.XPATH,
            value='//div[@id="labelEditModal"]/div/div/form/div/button'
        )
        button.click()

        # A success message will display
        body = self.browser.find_element(by=By.TAG_NAME, value='body')
        self.assertIn(
            'Client edited successfully.',
            body.text
        )

    # going to clients edit label - update duplicated email
    def test_board_clients_login_in_edit_label_duplicated_email(self):
        self.make_client(
            user=User.objects.get(id=self.user.id),
            cli_name='Second Client',
            cli_slug='newslug',
            country=Country.objects.get(id=self.country.id),
            state=State.objects.get(id=self.state.id),
            cli_email='mail1@email.com',
            cli_phone='1234567890',
            cli_responsible='Responsible'
        )

        # Initialiazing test
        self._test_path()

        # User finds edit icon and click on it
        edit = self.browser.find_element(
            by=By.XPATH, value='//a[@data-bs-target=".labelEditModal"]'
        )
        edit.click()
        self.sleep(1)

        email = self.browser.find_element(
            by=By.XPATH,
            value='//input[@id="email"]'
        )
        email.click()

        # User writes on input
        email.clear()
        email.send_keys('mail1@email.com')

        # User finds button and click on it
        button = self.browser.find_element(
            by=By.XPATH,
            value='//div[@id="labelEditModal"]/div/div/form/div/button'
        )
        button.click()

        # An error message will display
        body = self.browser.find_element(by=By.TAG_NAME, value='body')
        self.assertIn(
            'This email is already register in our database and cannot be used.',  # noqa: E501
            body.text
        )

    # going to clients edit label - update bad email
    def test_board_clients_login_in_edit_label_bad_email(self):
        # Initialiazing test
        self._test_path()

        # User finds edit icon and click on it
        edit = self.browser.find_element(
            by=By.XPATH, value='//a[@data-bs-target=".labelEditModal"]'
        )
        edit.click()
        self.sleep(1)

        email = self.browser.find_element(
            by=By.XPATH,
            value='//input[@id="email"]'
        )
        email.click()

        # User writes on input
        email.send_keys('Nada;')

        # User finds button and click on it
        button = self.browser.find_element(
            by=By.XPATH,
            value='//div[@id="labelEditModal"]/div/div/form/div/button'
        )
        button.click()

        # An error message will display
        modal = self.browser.find_element(
            by=By.XPATH,
            value='//div[@id="labelEditModal"]'
        )
        self.assertIn(
            'Email provided is invalid', modal.text
        )

    # going to clients edit label - update incomplete email
    def test_board_clients_login_in_edit_label_incomplete_email(self):
        # Initialiazing test
        self._test_path()

        # User finds edit icon and click on it
        edit = self.browser.find_element(
            by=By.XPATH, value='//a[@data-bs-target=".labelEditModal"]'
        )
        edit.click()
        self.sleep(1)

        email = self.browser.find_element(
            by=By.XPATH,
            value='//input[@id="email"]'
        )
        email.click()

        # User writes on input
        email.send_keys('nada@')

        # User finds button and click on it
        button = self.browser.find_element(
            by=By.XPATH,
            value='//div[@id="labelEditModal"]/div/div/form/div/button'
        )
        button.click()

        # An error message will display
        modal = self.browser.find_element(
            by=By.XPATH,
            value='//div[@id="labelEditModal"]'
        )
        self.assertIn(
            'Email provided is invalid', modal.text
        )

    # going to clients edit label - update valid email
    def test_board_clients_login_in_edit_label_valid_email(self):
        # Initialiazing test
        self._test_path()

        # User finds edit icon and click on it
        edit = self.browser.find_element(
            by=By.XPATH, value='//a[@data-bs-target=".labelEditModal"]'
        )
        edit.click()
        self.sleep(1)

        email = self.browser.find_element(
            by=By.XPATH,
            value='//input[@id="email"]'
        )
        email.click()

        # User writes on input
        email.clear()
        email.send_keys('nada@nada.com')

        # User finds button and click on it
        button = self.browser.find_element(
            by=By.XPATH,
            value='//div[@id="labelEditModal"]/div/div/form/div/button'
        )
        button.click()

        # A success message will display
        body = self.browser.find_element(by=By.TAG_NAME, value='body')
        self.assertIn(
            'Client edited successfully.',
            body.text
        )

    # going to clients edit label - update bad phone
    def test_board_clients_login_in_edit_label_bad_phone(self):
        # Initialiazing test
        self._test_path()

        # User finds edit icon and click on it
        edit = self.browser.find_element(
            by=By.XPATH, value='//a[@data-bs-target=".labelEditModal"]'
        )
        edit.click()
        self.sleep(1)

        phone = self.browser.find_element(
            by=By.XPATH,
            value='//input[@id="phone"]'
        )
        phone.click()

        # User writes on input
        phone.send_keys(';;;')

        # User finds button and click on it
        button = self.browser.find_element(
            by=By.XPATH,
            value='//div[@id="labelEditModal"]/div/div/form/div/button'
        )
        button.click()

        # An error message will display
        body = self.browser.find_element(by=By.TAG_NAME, value='body')
        self.assertIn(
            'Entry cannot contain disallowed characters. e.g. ";".',
            body.text
        )

    # going to clients edit label - update incomplete phone
    def test_board_clients_login_in_edit_label_incomplete_phone(self):
        # Initialiazing test
        self._test_path()

        # User finds edit icon and click on it
        edit = self.browser.find_element(
            by=By.XPATH, value='//a[@data-bs-target=".labelEditModal"]'
        )
        edit.click()
        self.sleep(1)

        phone = self.browser.find_element(
            by=By.XPATH,
            value='//input[@id="phone"]'
        )
        phone.click()

        # User writes on input
        phone.send_keys('1234')

        # User finds button and click on it
        button = self.browser.find_element(
            by=By.XPATH,
            value='//div[@id="labelEditModal"]/div/div/form/div/button'
        )
        button.click()

        # An error message will display
        body = self.browser.find_element(by=By.TAG_NAME, value='body')
        self.assertIn(
            'Invalid phone number.',
            body.text
        )

    # going to clients edit label - update valid phone
    def test_board_clients_login_in_edit_label_valid_phone(self):
        # Initialiazing test
        self._test_path()

        # User finds edit icon and click on it
        edit = self.browser.find_element(
            by=By.XPATH, value='//a[@data-bs-target=".labelEditModal"]'
        )
        edit.click()
        self.sleep(1)

        phone = self.browser.find_element(
            by=By.XPATH,
            value='//input[@id="phone"]'
        )
        phone.click()

        # User writes on input
        phone.clear()
        phone.send_keys('1234567888')

        # User finds button and click on it
        button = self.browser.find_element(
            by=By.XPATH,
            value='//div[@id="labelEditModal"]/div/div/form/div/button'
        )
        button.click()

        # A success message will display
        body = self.browser.find_element(by=By.TAG_NAME, value='body')
        self.assertIn(
            'Client edited successfully.',
            body.text
        )

    # going to clients edit label - update bad responsible
    def test_board_clients_login_in_edit_label_bad_responsible(self):
        # Initialiazing test
        self._test_path()

        # User finds edit icon and click on it
        edit = self.browser.find_element(
            by=By.XPATH, value='//a[@data-bs-target=".labelEditModal"]'
        )
        edit.click()
        self.sleep(1)

        responsible = self.browser.find_element(
            by=By.XPATH,
            value='//input[@id="responsible"]'
        )
        responsible.click()

        # User writes on input
        responsible.send_keys('Responsible;;;')

        # User finds button and click on it
        button = self.browser.find_element(
            by=By.XPATH,
            value='//div[@id="labelEditModal"]/div/div/form/div/button'
        )
        button.click()

        # An error message will display
        modal = self.browser.find_element(
            by=By.XPATH,
            value='//div[@id="labelEditModal"]'
        )
        self.assertIn(
            'Entry cannot contain disallowed characters. e.g. ";"', modal.text
        )

    # going to clients edit label - update valid responsible
    def test_board_clients_login_in_edit_label_valid_responsible(self):
        # Initialiazing test
        self._test_path()

        # User finds edit icon and click on it
        edit = self.browser.find_element(
            by=By.XPATH, value='//a[@data-bs-target=".labelEditModal"]'
        )
        edit.click()
        self.sleep(1)

        responsible = self.browser.find_element(
            by=By.XPATH,
            value='//input[@id="responsible"]'
        )
        responsible.click()

        # User writes on input
        responsible.clear()
        responsible.send_keys('Valid Responsible')

        # User finds button and click on it
        button = self.browser.find_element(
            by=By.XPATH,
            value='//div[@id="labelEditModal"]/div/div/form/div/button'
        )
        button.click()

        # A success message will display
        body = self.browser.find_element(by=By.TAG_NAME, value='body')
        self.assertIn(
            'Client edited successfully.',
            body.text
        )

    # going to clients delete label
    def test_board_clients_login_in_delete_label(self):
        # Initialiazing test
        self._test_path()

        # User finds delete icon and click on it
        delete = self.browser.find_element(
            by=By.XPATH, value='//a[@data-bs-target=".labelRemoveModal"]'
        )
        delete.click()
        self.sleep(1)

        # A removal modal will display and user will check Client
        modal = self.browser.find_element(
            by=By.XPATH,
            value='//div[@id="labelRemoveModal"]/div/div/form/div/p[@class="mb-4 modal_client"]/span'  # noqa: E501
        )
        self.assertIn('Client', modal.text)

        # Than check Country
        modal = self.browser.find_element(
            by=By.XPATH,
            value='//div[@id="labelRemoveModal"]/div/div/form/div/div/p[@class="mb-2 modal_region"]/span'  # noqa: E501
        )
        self.assertIn('Country', modal.text)

        # Than check State
        modal = self.browser.find_element(
            by=By.XPATH,
            value='//div[@id="labelRemoveModal"]/div/div/form/div/p[@class="mb-2 modal_state"]/span'  # noqa: E501
        )
        self.assertIn('State', modal.text)

        # Than check City
        modal = self.browser.find_element(
            by=By.XPATH,
            value='//div[@id="labelRemoveModal"]/div/div/form/div/p[@class="mb-4 modal_city"]/span'  # noqa: E501
        )
        self.assertIn('City', modal.text)

        # Than check Email
        modal = self.browser.find_element(
            by=By.XPATH,
            value='//div[@id="labelRemoveModal"]/div/div/form/div/div/p[@class="mb-2 modal_email"]/span'  # noqa: E501
        )
        self.assertIn('mail@email.com', modal.text)

        # Than check Phone
        modal = self.browser.find_element(
            by=By.XPATH,
            value='//div[@id="labelRemoveModal"]/div/div/form/div/div/p[@class="mb-2 modal_phone"]/span'  # noqa: E501
        )
        self.assertIn('1234567890', modal.text)

        # Than check Responsible
        modal = self.browser.find_element(
            by=By.XPATH,
            value='//div[@id="labelRemoveModal"]/div/div/form/div/div/p[@class="mb-2 modal_responsible"]/span'  # noqa: E501
        )
        self.assertIn('Responsible', modal.text)

        # User finds removal button and click on it
        button = self.browser.find_element(
            by=By.XPATH,
            value='//div[@id="labelRemoveModal"]/div/div/form/div/button[@type="submit"]'  # noqa: E501
        )
        button.click()

        # An success message will display
        body = self.browser.find_element(by=By.TAG_NAME, value='body')
        self.assertIn(
            'Client removed successfully.',
            body.text
        )
