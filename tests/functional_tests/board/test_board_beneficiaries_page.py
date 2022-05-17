import pytest
from home.models import User
from home.tests.test_home_helper import HomeHelperMixin
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from tests.functional_tests.home.test_home_base_helper import TestHelperStatic

from board.models import BeneficiaryCategory
from board.tests.test_board_helper import BoardHelperMixin


@pytest.mark.selenium
class TestBoardBeneficiariesPage(TestHelperStatic, HomeHelperMixin,
                                 BoardHelperMixin):
    """
    These tests are being created based on StaticLiveServerTestCase
    That is, with CSS and JS files
    """
    def setUp(self) -> None:
        self.user = self.make_user(use_is_valid=True)
        self.category = self.make_beneficiary_category(
            user=User.objects.get(id=self.user.id)
        )
        self.make_beneficiary(
            user=User.objects.get(id=self.user.id),
            beneficiary_category=BeneficiaryCategory.objects.get(
                id=self.category.id
            )
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

        # User finds sidebar beneficieries and click on it
        sidebar_beneficieries = self.browser.find_element(
            by=By.XPATH, value='//a[@key="t-beneficiaries"]'
        )
        self.sleep(1)
        sidebar_beneficieries.click()

    # Testing user login in with a existing email of a validated user
    # going to beneficieries view details
    def test_board_beneficiaries_login_in_view_details(self):
        # Initialiazing test
        self._test_path()

        # User finds view details and click on it
        view = self.browser.find_element(
            by=By.XPATH, value='//button[@data-bs-target=".labelDetailsModal"]'
        )
        view.click()
        self.sleep(1)

        # A view description will display and user will check
        # Beneficiary Category
        modal = self.browser.find_element(
            by=By.XPATH,
            value='//p[@class="mb-2 modal_description"]/span'
        )
        self.assertIn('Description', modal.text)

        # Than check Beneficiary Name
        modal = self.browser.find_element(
            by=By.XPATH,
            value='//p[@class="mb-2 modal_name"]/span'
        )
        self.assertIn('Beneficiary', modal.text)

    # going to beneficieries edit label - update same name
    def test_board_beneficiaries_login_in_edit_label_same_name(self):
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

        # An error message will display
        body = self.browser.find_element(by=By.TAG_NAME, value='body')
        self.assertIn(
            'Beneficiary name edited successfully.',
            body.text
        )

    # going to beneficieries edit label - update empty name
    def test_board_beneficiaries_login_in_edit_label_empty_name(self):
        # Initialiazing test
        self._test_path()

        # User finds edit icon and click on it
        edit = self.browser.find_element(
            by=By.XPATH, value='//a[@data-bs-target=".labelEditModal"]'
        )
        edit.click()
        self.sleep(1)

        # User finds name input area and click on it
        name = self.browser.find_element(
            by=By.XPATH,
            value='//input[@id="name"]'
        )
        name.click()

        # User clear input
        name.clear()

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
        self.assertIn('Please enter beneficiary name', modal.text)

    # going to beneficieries edit label - update bad name
    def test_board_beneficiaries_login_in_edit_label_bad_name(self):
        # Initialiazing test
        self._test_path()

        # User finds edit icon and click on it
        edit = self.browser.find_element(
            by=By.XPATH, value='//a[@data-bs-target=".labelEditModal"]'
        )
        edit.click()
        self.sleep(1)

        # User finds name input area and click on it
        name = self.browser.find_element(
            by=By.XPATH,
            value='//input[@id="name"]'
        )
        name.click()

        # User clear input
        name.send_keys('Nada;')

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

    # going to beneficieries edit label - update valid name
    def test_board_beneficiaries_login_in_edit_label_valid_name(self):
        # Initialiazing test
        self._test_path()

        # User finds edit icon and click on it
        edit = self.browser.find_element(
            by=By.XPATH, value='//a[@data-bs-target=".labelEditModal"]'
        )
        edit.click()
        self.sleep(1)

        # User finds name input area and click on it
        name = self.browser.find_element(
            by=By.XPATH,
            value='//input[@id="name"]'
        )
        name.click()

        # User clear input and edit name
        name.clear()
        name.send_keys('Nada')

        # User finds button and click on it
        button = self.browser.find_element(
            by=By.XPATH,
            value='//div[@id="labelEditModal"]/div/div/form/div/button'
        )
        button.click()

        # An success message will display
        body = self.browser.find_element(by=By.TAG_NAME, value='body')
        self.assertIn(
            'Beneficiary name edited successfully.',
            body.text
        )

    # going to beneficieries edit label - update same type
    def test_board_beneficiaries_login_in_edit_label_same_type(self):
        # Initialiazing test
        self._test_path()

        # User finds edit icon and click on it
        edit = self.browser.find_element(
            by=By.XPATH, value='//a[@data-bs-target=".labelEditModal"]'
        )
        edit.click()
        self.sleep(1)

        # User finds checkbox and click on it
        checkbox = self.browser.find_element(
            by=By.XPATH,
            value='//input[@id="checkbox_edit"]'
        )
        checkbox.click()

        # User finds button and click on it
        button = self.browser.find_element(
            by=By.XPATH,
            value='//div[@id="labelEditModal"]/div/div/form/div/button'
        )
        button.click()

        # An error message will display
        body = self.browser.find_element(by=By.TAG_NAME, value='body')
        self.assertIn(
            'Beneficiary type and name edited successfully.',
            body.text
        )

    # going to beneficieries edit label - update empty type
    def test_board_beneficiaries_login_in_edit_label_empty_type(self):
        # Initialiazing test
        self._test_path()

        # User finds edit icon and click on it
        edit = self.browser.find_element(
            by=By.XPATH, value='//a[@data-bs-target=".labelEditModal"]'
        )
        edit.click()
        self.sleep(1)

        # User finds checkbox and click on it
        checkbox = self.browser.find_element(
            by=By.XPATH,
            value='//input[@id="checkbox_edit"]'
        )
        checkbox.click()

        # User finds type input area and click on it
        type = self.browser.find_element(
            by=By.XPATH,
            value='//input[@id="description"]'
        )
        type.click()

        # User clear input
        type.clear()

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
            'Please enter type name', modal.text
        )

    # going to beneficieries edit label - update bad type
    def test_board_beneficiaries_login_in_edit_label_bad_type(self):
        # Initialiazing test
        self._test_path()

        # User finds edit icon and click on it
        edit = self.browser.find_element(
            by=By.XPATH, value='//a[@data-bs-target=".labelEditModal"]'
        )
        edit.click()
        self.sleep(1)

        # User finds checkbox and click on it
        checkbox = self.browser.find_element(
            by=By.XPATH,
            value='//input[@id="checkbox_edit"]'
        )
        checkbox.click()

        # User finds type input area and click on it
        type = self.browser.find_element(
            by=By.XPATH,
            value='//input[@id="description"]'
        )
        type.click()

        # User clear input
        type.send_keys('Nada;')

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

    # going to beneficieries edit label - update valid type
    def test_board_beneficiaries_login_in_edit_label_valid_type(self):
        # Initialiazing test
        self._test_path()

        # User finds edit icon and click on it
        edit = self.browser.find_element(
            by=By.XPATH, value='//a[@data-bs-target=".labelEditModal"]'
        )
        edit.click()
        self.sleep(1)

        # User finds checkbox and click on it
        checkbox = self.browser.find_element(
            by=By.XPATH,
            value='//input[@id="checkbox_edit"]'
        )
        checkbox.click()

        # User finds type input area and click on it
        type = self.browser.find_element(
            by=By.XPATH,
            value='//input[@id="description"]'
        )
        type.click()

        # User clear input and edit type
        type.clear()
        type.send_keys('Nada')

        # User finds button and click on it
        button = self.browser.find_element(
            by=By.XPATH,
            value='//div[@id="labelEditModal"]/div/div/form/div/button'
        )
        button.click()

        # An success message will display
        body = self.browser.find_element(by=By.TAG_NAME, value='body')
        self.assertIn(
            'Beneficiary type and name edited successfully.',
            body.text
        )

    # going to beneficieries delete label
    def test_board_beneficiaries_login_in_delete_label(self):
        # Initialiazing test
        self._test_path()

        # User finds delete icon and click on it
        delete = self.browser.find_element(
            by=By.XPATH, value='//a[@data-bs-target=".labelRemoveModal"]'
        )
        delete.click()
        self.sleep(1)

        # A removal modal will display and user will check
        # Beneficiary Category
        modal = self.browser.find_element(
            by=By.XPATH,
            value='//div[@id="labelRemoveModal"]/div/div/form/div/p[@class="mb-2 modal_description"]/span'  # noqa: E501
        )
        self.assertIn('Description', modal.text)

        # Than check Beneficiary Name
        modal = self.browser.find_element(
            by=By.XPATH,
            value='//div[@id="labelRemoveModal"]/div/div/form/div/p[@class="mb-2 modal_name"]/span'  # noqa: E501
        )
        self.assertIn('Beneficiary', modal.text)

        # User finds removal button and click on it
        button = self.browser.find_element(
            by=By.XPATH,
            value='//div[@id="labelRemoveModal"]/div/div/form/div/button[@type="submit"]'  # noqa: E501
        )
        button.click()

        # An success message will display
        body = self.browser.find_element(by=By.TAG_NAME, value='body')
        self.assertIn(
            'Beneficiary name removed successfully.',
            body.text
        )

    # going to beneficieries edit label - update valid type
    def test_board_beneficiaries_login_in_edit_default_category(self):
        data = BeneficiaryCategory.objects.all()[0]
        data.user_id = None
        data.save()

        # Initialiazing test
        self._test_path()

        # User finds edit icon and click on it
        edit = self.browser.find_element(
            by=By.XPATH, value='//a[@data-bs-target=".labelEditModal"]'
        )
        edit.click()
        self.sleep(1)

        # User finds checkbox and click on it
        checkbox = self.browser.find_element(
            by=By.XPATH,
            value='//input[@id="checkbox_edit"]'
        )
        checkbox.click()

        # User finds type input area and click on it
        type = self.browser.find_element(
            by=By.XPATH,
            value='//input[@id="description"]'
        )
        type.click()

        # User clear input and edit type
        type.clear()
        type.send_keys('Nada')

        # User finds button and click on it
        button = self.browser.find_element(
            by=By.XPATH,
            value='//div[@id="labelEditModal"]/div/div/form/div/button'
        )
        button.click()

        # An error message will display
        body = self.browser.find_element(by=By.TAG_NAME, value='body')
        self.assertIn(
            'Editing default types is prohibited.',
            body.text
        )
