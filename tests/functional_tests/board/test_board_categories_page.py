import pytest
from home.models import User
from home.tests.test_home_helper import HomeHelperMixin
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from tests.functional_tests.home.test_home_base_helper import TestHelperStatic

from board.models import Category
from board.tests.test_board_helper import BoardHelperMixin


@pytest.mark.selenium
class TestBoardCategoriesPage(TestHelperStatic, HomeHelperMixin,
                              BoardHelperMixin):
    """
    These tests are being created based on StaticLiveServerTestCase
    That is, with CSS and JS files
    """
    def setUp(self) -> None:
        self.user = self.make_user(use_is_valid=True)
        self.category = self.make_category(
            user=User.objects.get(id=self.user.id)
        )
        self.make_subcategory(
            category=Category.objects.get(id=self.category.id),
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

        # User finds sidebar categories and click on it
        sidebar_categories = self.browser.find_element(
            by=By.XPATH, value='//a[@key="t-categories"]'
        )
        self.sleep(1)
        sidebar_categories.click()

    # Testing user login in with a existing email of a validated user
    # going to categories view details
    def test_board_categories_login_in_view_details(self):
        # Initialiazing test
        self._test_path()

        # User finds view details and click on it
        view = self.browser.find_element(
            by=By.XPATH, value='//button[@data-bs-target=".labelDetailsModal"]'
        )
        view.click()
        self.sleep(1)

        # A view description will display and user will check Category
        modal = self.browser.find_element(
            by=By.XPATH,
            value='//p[@class="mb-2 modal_category"]/span'
        )
        self.assertIn('Category', modal.text)

        # Than check Subcategory
        modal = self.browser.find_element(
            by=By.XPATH,
            value='//p[@class="mb-2 modal_subcategory"]/span'
        )
        self.assertIn('Subcategory', modal.text)

    # going to categories edit label - update same subcategory
    def test_board_categories_login_in_edit_label_same_subcategory(self):
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
            'Subcategory edited successfully.',
            body.text
        )

    # going to categories edit label - update empty subcategory
    def test_board_categories_login_in_edit_label_empty_subcategory(self):
        # Initialiazing test
        self._test_path()

        # User finds edit icon and click on it
        edit = self.browser.find_element(
            by=By.XPATH, value='//a[@data-bs-target=".labelEditModal"]'
        )
        edit.click()
        self.sleep(1)

        # User finds subcategory input area and click on it
        name = self.browser.find_element(
            by=By.XPATH,
            value='//input[@id="subname"]'
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
        self.assertIn('Please enter subcategory name', modal.text)

    # going to categories edit label - update bad subcategory
    def test_board_categories_login_in_edit_label_bad_subcategory(self):
        # Initialiazing test
        self._test_path()

        # User finds edit icon and click on it
        edit = self.browser.find_element(
            by=By.XPATH, value='//a[@data-bs-target=".labelEditModal"]'
        )
        edit.click()
        self.sleep(1)

        # User finds subcategory input area and click on it
        name = self.browser.find_element(
            by=By.XPATH,
            value='//input[@id="subname"]'
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

    # going to categories edit label - update valid subcategory
    def test_board_categories_login_in_edit_label_valid_subcategory(self):
        # Initialiazing test
        self._test_path()

        # User finds edit icon and click on it
        edit = self.browser.find_element(
            by=By.XPATH, value='//a[@data-bs-target=".labelEditModal"]'
        )
        edit.click()
        self.sleep(1)

        # User finds subcategory input area and click on it
        name = self.browser.find_element(
            by=By.XPATH,
            value='//input[@id="subname"]'
        )
        name.click()

        # User clear input and edit subcategory
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
            'Subcategory edited successfully.',
            body.text
        )

    # going to categories edit label - update same category
    def test_board_categories_login_in_edit_label_same_category(self):
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
            'Category and subcategory edited successfully.',
            body.text
        )

    # going to categories edit label - update empty category
    def test_board_categories_login_in_edit_label_empty_category(self):
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

        # User finds category input area and click on it
        category = self.browser.find_element(
            by=By.XPATH,
            value='//input[@id="name"]'
        )
        category.click()

        # User clear input
        category.clear()

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
            'Please enter category name', modal.text
        )

    # going to categories edit label - update bad category
    def test_board_categories_login_in_edit_label_bad_category(self):
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

        # User finds category input area and click on it
        category = self.browser.find_element(
            by=By.XPATH,
            value='//input[@id="name"]'
        )
        category.click()

        # User clear input
        category.send_keys('Nada;')

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

    # going to categories edit label - update valid category
    def test_board_categories_login_in_edit_label_valid_category(self):
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

        # User finds category input area and click on it
        category = self.browser.find_element(
            by=By.XPATH,
            value='//input[@id="name"]'
        )
        category.click()

        # User clear input and edit category
        category.clear()
        category.send_keys('Nada')

        # User finds button and click on it
        button = self.browser.find_element(
            by=By.XPATH,
            value='//div[@id="labelEditModal"]/div/div/form/div/button'
        )
        button.click()

        # An success message will display
        body = self.browser.find_element(by=By.TAG_NAME, value='body')
        self.assertIn(
            'Category and subcategory edited successfully.',
            body.text
        )

    # going to categories delete label
    def test_board_categories_login_in_delete_label(self):
        # Initialiazing test
        self._test_path()

        # User finds delete icon and click on it
        delete = self.browser.find_element(
            by=By.XPATH, value='//a[@data-bs-target=".labelRemoveModal"]'
        )
        delete.click()
        self.sleep(1)

        # A removal modal will display and user will check Category
        modal = self.browser.find_element(
            by=By.XPATH,
            value='//div[@id="labelRemoveModal"]/div/div/form/div/p[@class="mb-2 modal_category"]/span'  # noqa: E501
        )
        self.assertIn('Category', modal.text)

        # Than check Subcategory
        modal = self.browser.find_element(
            by=By.XPATH,
            value='//div[@id="labelRemoveModal"]/div/div/form/div/p[@class="mb-2 modal_subcategory"]/span'  # noqa: E501
        )
        self.assertIn('Subcategory', modal.text)

        # User finds removal button and click on it
        button = self.browser.find_element(
            by=By.XPATH,
            value='//div[@id="labelRemoveModal"]/div/div/form/div/button[@type="submit"]'  # noqa: E501
        )
        button.click()

        # An success message will display
        body = self.browser.find_element(by=By.TAG_NAME, value='body')
        self.assertIn(
            'Subcategory removed successfully.',
            body.text
        )
