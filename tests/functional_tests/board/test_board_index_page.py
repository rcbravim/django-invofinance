import pytest
from home.models import User
from home.tests.test_home_helper import HomeHelperMixin
from library.utils.helper import hash_gen
from parameterized import parameterized
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from tests.functional_tests.home.test_home_base_helper import TestHelperStatic

from board.models import (Beneficiary, BeneficiaryCategory, Category, Client,
                          Country, Financial, State, SubCategory)
from board.tests.test_board_helper import BoardHelperMixin


@pytest.mark.selenium
class TestBoardIndexPage(TestHelperStatic, HomeHelperMixin,
                         BoardHelperMixin):
    """
    These tests are being created based on StaticLiveServerTestCase
    That is, with CSS and JS files
    """
    def setUp(self) -> None:
        self.user = self.make_user(use_is_valid=True)
        self.category_income = self.make_category(
            user=User.objects.get(id=self.user.id),
        )
        self.category_expense = self.make_category(
            user=User.objects.get(id=self.user.id),
            cat_name='CategoryExpense',
            cat_slug='slug_expense',
            cat_type=2
        )
        self.subcategory_income = self.make_subcategory(
            category=Category.objects.get(id=self.category_income.id)
        )
        self.subcategory_expense = self.make_subcategory(
            category=Category.objects.get(id=self.category_expense.id),
            sub_slug='slug_expense',
        )
        self.beneficiary_category = self.make_beneficiary_category(
            user=User.objects.get(id=self.user.id)
        )
        self.beneficiary = self.make_beneficiary(
            user=User.objects.get(id=self.user.id),
            beneficiary_category=BeneficiaryCategory.objects.get(
                id=self.beneficiary_category.id
            )
        )
        self.country = self.make_country()
        self.state = self.make_state(
            country=Country.objects.get(id=self.country.id)
        )
        self.client_label = self.make_client(
            user=User.objects.get(id=self.user.id),
            country=Country.objects.get(id=self.country.id),
            state=State.objects.get(id=self.state.id),
        )
        self.cost_center = self.make_financial(
            user=User.objects.get(id=self.user.id),
            fin_cost_center='Cost Center',
            fin_description='Description',
            fin_type=1
        )
        self.bank_account = self.make_financial(
            user=User.objects.get(id=self.user.id),
            fin_slug=hash_gen('bank_slug'),
            fin_bank_name='Bank Name',
            fin_bank_branch='1234',
            fin_bank_account='123456789',
            fin_type=2
        )
        self.make_release(
            user=User.objects.get(id=self.user.id),
            subcategory=SubCategory.objects.get(id=self.subcategory_income.id),
            beneficiary=Beneficiary.objects.get(id=self.beneficiary.id),
            client=Client.objects.get(id=self.client_label.id),
            financial_cost_center=Financial.objects.get(id=self.cost_center.id),  # noqa: E501
            financial_account=Financial.objects.get(id=self.bank_account.id),
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

        # An successful message will display
        body = self.browser.find_element(by=By.TAG_NAME, value='body')
        self.assertIn('You are logged in.', body.text)

        # User pass month and year parameters on URL
        self.browser.execute_script('window.location.href += "?y=2022&m=05"')
        self.sleep(1)

    # Testing user login in with a existing email of a validated user
    # going to index view details
    def test_board_index_login_in_view_details(self):
        # Initialiazing test
        self._test_path()

        # User finds view details and click on it
        view = self.browser.find_element(
            by=By.XPATH, value='//button[@data-bs-target=".labelDetailsModal"]'
        )
        view.click()
        self.sleep(1)

        # A entry view will display and user will check:
        # Index Entry Date
        modal = self.browser.find_element(
            by=By.XPATH,
            value='//p[@class="mb-2 modal_entry_date"]/span'
        )
        self.assertIn('05/01/2022', modal.text)

        # Index Badge
        modal = self.browser.find_element(
            by=By.XPATH,
            value='//span[@class="modal_entry_status badge badge-pill font-size-12 mb-2 badge-soft-success"]'  # noqa: E501
        )
        self.assertIn('Received', modal.text)

        # Than check Index Amount
        modal = self.browser.find_element(
            by=By.XPATH,
            value='//p[@class="modal_entry_amount mb-4"]/span'
        )
        self.assertIn('$1,000.00', modal.text)

        # Than check Index Category
        modal = self.browser.find_element(
            by=By.XPATH,
            value='//p[@class="mb-2 modal_category"]/span'
        )
        self.assertIn('Category', modal.text)

        # Index Category Badge
        modal = self.browser.find_element(
            by=By.XPATH,
            value='//span[@class="modal_category_type badge badge-pill font-size-12 mb-2 badge-soft-success"]'  # noqa: E501
        )
        self.assertIn('Income', modal.text)

        # Than check Index SubCategory
        modal = self.browser.find_element(
            by=By.XPATH,
            value='//p[@class="mb-4 modal_subcategory"]/span'
        )
        self.assertIn('Subcategory', modal.text)

        # Than check Index Beneficiary Category
        modal = self.browser.find_element(
            by=By.XPATH,
            value='//p[@class="mb-2 modal_beneficiary_category"]/span'
        )
        self.assertIn('Description', modal.text)

        # Than check Index Beneficiary Name
        modal = self.browser.find_element(
            by=By.XPATH,
            value='//p[@class="mb-4 modal_beneficiary_name"]/span'
        )
        self.assertIn('Beneficiary', modal.text)

        # Than check Index Bank Name
        modal = self.browser.find_element(
            by=By.XPATH,
            value='//p[@class="mb-2 modal_bank"]/span'
        )
        self.assertIn('Bank Name', modal.text)

        # Than check Index Bank Branch
        modal = self.browser.find_element(
            by=By.XPATH,
            value='//p[@class="mb-2 modal_branch"]/span'
        )
        self.assertIn('1234', modal.text)

        # Than check Index Bank Account
        modal = self.browser.find_element(
            by=By.XPATH,
            value='//p[@class="mb-4 modal_account"]/span'
        )
        self.assertIn('123456789', modal.text)

        # Than check Index Cost Center
        modal = self.browser.find_element(
            by=By.XPATH,
            value='//p[@class="mb-2 modal_cost_center"]/span'
        )
        self.assertIn('Cost Center', modal.text)

        # Than check Index Cost Center Description
        modal = self.browser.find_element(
            by=By.XPATH,
            value='//p[@class="modal_description mb-4"]/span'
        )
        self.assertIn('Description', modal.text)

        # Than check Index Client Name
        modal = self.browser.find_element(
            by=By.XPATH,
            value='//p[@class="mb-4 modal_client"]/span'
        )
        self.assertIn('Client', modal.text)

        # Than check Index Client Country
        modal = self.browser.find_element(
            by=By.XPATH,
            value='//p[@class="mb-2 modal_region"]/span'
        )
        self.assertIn('Country', modal.text)

        # Than check Index Client State
        modal = self.browser.find_element(
            by=By.XPATH,
            value='//p[@class="mb-2 modal_state"]/span'
        )
        self.assertIn('State', modal.text)

        # Than check Index Client City
        modal = self.browser.find_element(
            by=By.XPATH,
            value='//p[@class="mb-2 modal_city"]/span'
        )
        self.assertIn('City', modal.text)

    # going to index new entry - leaving everything empty
    def test_board_index_login_new_entry_all_empty(self):
        # Initialiazing test
        self._test_path()

        # User finds add icon and click on it
        edit = self.browser.find_element(
            by=By.XPATH, value='//button[@data-bs-target=".newEntryModal"]'
        )
        edit.click()
        self.sleep(1)

        # User finds button and click on it
        button = self.browser.find_element(
            by=By.XPATH,
            value='//div[@id="newEntryModal"]/div/div/form/div/button'
        )
        button.click()

        # Multiple error messages will display
        modal = self.browser.find_element(
            by=By.XPATH,
            value='//div[@id="newEntryModal"]'
        )
        self.assertIn('Please enter entry date', modal.text)
        self.assertIn('Please select a category', modal.text)
        self.assertIn('Please select a subcategory', modal.text)
        self.assertIn(
            "Please select a beneficiary, even if it's yourself", modal.text
        )
        self.assertIn("Please select a account, even if it's cash", modal.text)
        self.assertIn('Please enter entry amount', modal.text)

    # going to index new entry - adding entry date with bad data
    @parameterized.expand([
        (';;;;;'),  # invalid data
        ('31-02-2022'),  # invalid date
        ('15-01-202222'),  # invalid date
    ])
    def test_board_index_login_new_entry_date_errors(self, value):
        # Initialiazing test
        self._test_path()

        # User finds add icon and click on it
        edit = self.browser.find_element(
            by=By.XPATH, value='//button[@data-bs-target=".newEntryModal"]'
        )
        edit.click()
        self.sleep(1)

        # User finds entry_date input area and click on it
        entry_date = self.browser.find_element(
            by=By.XPATH,
            value='//input[@id="entry_date"]'
        )
        entry_date.click()

        # User clear input and send new value
        entry_date.clear()
        entry_date.send_keys(value)

        # User finds button and click on it
        button = self.browser.find_element(
            by=By.XPATH,
            value='//div[@id="newEntryModal"]/div/div/form/div/button'
        )
        button.click()

        # Multiple error messages will display
        modal = self.browser.find_element(
            by=By.XPATH,
            value='//div[@id="newEntryModal"]'
        )
        if '202222' in value:
            self.assertIn('Date provided is invalid', modal.text)
        else:
            self.assertIn('Please enter entry date', modal.text)

    # going to index new entry - adding description with bad data
    def test_board_index_login_new_description_error(self):
        # Initialiazing test
        self._test_path()

        # User finds add icon and click on it
        edit = self.browser.find_element(
            by=By.XPATH, value='//button[@data-bs-target=".newEntryModal"]'
        )
        edit.click()
        self.sleep(1)

        # User finds description input area and click on it
        description = self.browser.find_element(
            by=By.XPATH,
            value='//input[@id="description"]'
        )
        description.click()

        # User clear input and send new value
        description.clear()
        description.send_keys('Description;;;')

        # User finds button and click on it
        button = self.browser.find_element(
            by=By.XPATH,
            value='//div[@id="newEntryModal"]/div/div/form/div/button'
        )
        button.click()

        # Multiple error messages will display
        modal = self.browser.find_element(
            by=By.XPATH,
            value='//div[@id="newEntryModal"]'
        )
        self.assertIn(
            'Entry cannot contain disallowed characters. e.g. ";"', modal.text
        )

    # going to index new entry - adding amount with bad data
    @parameterized.expand([
        (';;;;;'),  # invalid data
        ('teste@'),  # only string
    ])
    def test_board_index_login_new_amount_errors(self, value):
        # Initialiazing test
        self._test_path()

        # User finds add icon and click on it
        edit = self.browser.find_element(
            by=By.XPATH, value='//button[@data-bs-target=".newEntryModal"]'
        )
        edit.click()
        self.sleep(1)

        # User finds amount input area and click on it
        amount = self.browser.find_element(
            by=By.XPATH,
            value='//input[@id="amount"]'
        )
        amount.click()

        # User clear input and send new value
        amount.clear()
        amount.send_keys(value)

        # User finds button and click on it
        button = self.browser.find_element(
            by=By.XPATH,
            value='//div[@id="newEntryModal"]/div/div/form/div/button'
        )
        button.click()

        # Multiple error messages will display
        modal = self.browser.find_element(
            by=By.XPATH,
            value='//div[@id="newEntryModal"]'
        )
        self.assertIn('Please enter entry amount', modal.text)

    # going to index new entry - adding new entry
    def test_board_index_login_new_adding(self):
        # Initialiazing test
        self._test_path()

        # User finds add icon and click on it
        edit = self.browser.find_element(
            by=By.XPATH, value='//button[@data-bs-target=".newEntryModal"]'
        )
        edit.click()
        self.sleep(1)

        # User finds entry_date input area and click on it
        entry_date = self.browser.find_element(
            by=By.XPATH,
            value='//input[@id="entry_date"]'
        )
        entry_date.click()

        # User clear input and send new value
        entry_date.clear()
        entry_date.send_keys('02-01-2022')

        # User finds category select area and click on it
        self.browser.find_element(
            by=By.XPATH,
            value='//select[@id="category"]/option[text()="Category"]'
        ).click()
        self.sleep(1)

        # User finds beneficiary select area and click on it
        self.browser.find_element(
            by=By.XPATH,
            value='//select[@id="beneficiary"]/option[text()="DES-Beneficiary"]'  # noqa: E501
        ).click()

        # User finds account select area and click on it
        self.browser.find_element(
            by=By.XPATH,
            value='//select[@id="account"]/option[text()="Bank Name: 1234 / 123456789"]'  # noqa: E501
        ).click()

        # User finds amount input area and click on it
        amount = self.browser.find_element(
            by=By.XPATH,
            value='//input[@id="amount"]'
        )
        amount.click()

        # User clear input and send new value
        amount.clear()
        amount.send_keys('125099')

        # User finds button and click on it
        button = self.browser.find_element(
            by=By.XPATH,
            value='//div[@id="newEntryModal"]/div/div/form/div/button'
        )
        button.click()

        # An success message will display
        body = self.browser.find_element(by=By.TAG_NAME, value='body')
        self.assertIn(
            'New entry added successfully.', body.text
        )

    # going to index edit entry - editing entry date with bad and empty data
    @parameterized.expand([
        (''),  # empty data
        (';;;;;'),  # invalid data
        ('31-02-2022'),  # invalid date
        ('15-01-202222'),  # invalid date
    ])
    def test_board_index_login_edit_entry_date_errors(self, value):
        # Initialiazing test
        self._test_path()

        # User finds edit icon and click on it
        self.browser.find_element(
            by=By.XPATH, value='//a[@data-bs-target=".labelEditModal"]'
        ).click()
        self.sleep(1)

        # User finds entry_date input area and click on it
        entry_date = self.browser.find_element(
            by=By.XPATH,
            value='//input[@id="entry_date_edit"]'
        )
        entry_date.click()

        # User clear input and send new value
        entry_date.clear()
        entry_date.send_keys(value)

        # User finds button and click on it
        button = self.browser.find_element(
            by=By.XPATH,
            value='//div[@id="labelEditModal"]/div/div/form/div/button'
        )
        button.click()

        # Multiple error messages will display
        modal = self.browser.find_element(
            by=By.XPATH,
            value='//div[@id="labelEditModal"]'
        )
        if '202222' in value:
            self.assertIn('Date provided is invalid', modal.text)
        else:
            self.assertIn('Please enter entry date', modal.text)

    # going to index edit entry - editing description with bad data
    def test_board_index_login_edit_description_error(self):
        # Initialiazing test
        self._test_path()

        # User finds edit icon and click on it
        self.browser.find_element(
            by=By.XPATH, value='//a[@data-bs-target=".labelEditModal"]'
        ).click()
        self.sleep(1)

        # User finds description input area and click on it
        description = self.browser.find_element(
            by=By.XPATH,
            value='//input[@id="description_edit"]'
        )
        description.click()

        # User clear input and send new value
        description.clear()
        description.send_keys('Description;;;')

        # User finds button and click on it
        button = self.browser.find_element(
            by=By.XPATH,
            value='//div[@id="labelEditModal"]/div/div/form/div/button'
        )
        button.click()

        # Multiple error messages will display
        modal = self.browser.find_element(
            by=By.XPATH,
            value='//div[@id="labelEditModal"]'
        )
        self.assertIn(
            'Entry cannot contain disallowed characters. e.g. ";"', modal.text
        )

    # going to index edit entry - editing amount with bad data
    @parameterized.expand([
        (';;;;;'),  # invalid data
        ('teste@'),  # only string
    ])
    def test_board_index_login_edit_amount_errors(self, value):
        # Initialiazing test
        self._test_path()

        # User finds edit icon and click on it
        self.browser.find_element(
            by=By.XPATH, value='//a[@data-bs-target=".labelEditModal"]'
        ).click()
        self.sleep(1)

        # User finds amount input area and click on it
        amount = self.browser.find_element(
            by=By.XPATH,
            value='//input[@id="amount_edit"]'
        )
        amount.click()

        # User clear input and send new value
        amount.clear()
        amount.send_keys(value)

        # User finds button and click on it
        button = self.browser.find_element(
            by=By.XPATH,
            value='//div[@id="labelEditModal"]/div/div/form/div/button'
        )
        button.click()

        # Multiple error messages will display
        modal = self.browser.find_element(
            by=By.XPATH,
            value='//div[@id="labelEditModal"]'
        )
        self.assertIn('Please enter entry amount', modal.text)

    # going to index edit entry - editing entry correctly
    def test_board_index_login_editing(self):
        # Initialiazing test
        self._test_path()

        # User finds add icon and click on it
        # User finds edit icon and click on it
        self.browser.find_element(
            by=By.XPATH, value='//a[@data-bs-target=".labelEditModal"]'
        ).click()
        self.sleep(1)

        # User finds entry_date input area and click on it
        entry_date = self.browser.find_element(
            by=By.XPATH,
            value='//input[@id="entry_date_edit"]'
        )
        entry_date.click()

        # User clear input and send new value
        entry_date.clear()
        entry_date.send_keys('02-01-2022')

        """ # User finds category select area and click on it
        self.browser.find_element(
            by=By.XPATH,
            value='//select[@id="category"]/option[text()="Category"]'
        ).click()
        self.sleep(1)

        # User finds beneficiary select area and click on it
        self.browser.find_element(
            by=By.XPATH,
            value='//select[@id="beneficiary"]/option[text()="DES-Beneficiary"]'  # noqa: E501
        ).click()

        # User finds account select area and click on it
        self.browser.find_element(
            by=By.XPATH,
            value='//select[@id="account"]/option[text()="Bank Name: 1234 / 123456789"]'  # noqa: E501
        ).click() """

        # User finds amount input area and click on it
        amount = self.browser.find_element(
            by=By.XPATH,
            value='//input[@id="amount_edit"]'
        )
        amount.click()

        # User clear input and send new value
        amount.clear()
        amount.send_keys('125099')

        # User finds button and click on it
        button = self.browser.find_element(
            by=By.XPATH,
            value='//div[@id="labelEditModal"]/div/div/form/div/button'
        )
        button.click()

        # An success message will display
        body = self.browser.find_element(by=By.TAG_NAME, value='body')
        self.assertIn(
            'Entry edited successfully.', body.text
        )

    # going to entry delete
    def test_board_index_login_in_delete_entry(self):
        # Initialiazing test
        self._test_path()

        # User finds delete icon and click on it
        self.browser.find_element(
            by=By.XPATH, value='//a[@data-bs-target=".labelRemoveModal"]'
        ).click()
        self.sleep(2)

        # A removal modal will display and user will check:
        # Index Entry Date
        modal = self.browser.find_elements(
            by=By.XPATH,
            value='//p[@class="mb-2 modal_entry_date"]/span'
        )
        self.assertIn('05/01/2022', modal[1].text)

        # Index Badge
        modal = self.browser.find_elements(
            by=By.XPATH,
            value='//span[@class="modal_entry_status badge badge-pill font-size-12 mb-2 badge-soft-success"]'  # noqa: E501
        )
        self.assertIn('Received', modal[1].text)

        # Than check Index Amount
        modal = self.browser.find_elements(
            by=By.XPATH,
            value='//p[@class="modal_entry_amount mb-4"]/span'
        )
        self.assertIn('$1,000.00', modal[1].text)

        # Than check Index Category
        modal = self.browser.find_elements(
            by=By.XPATH,
            value='//p[@class="mb-2 modal_category"]/span'
        )
        self.assertIn('Category', modal[1].text)

        # Index Category Badge
        modal = self.browser.find_elements(
            by=By.XPATH,
            value='//span[@class="modal_category_type badge badge-pill font-size-12 mb-2 badge-soft-success"]'  # noqa: E501
        )
        self.assertIn('Income', modal[1].text)

        # Than check Index SubCategory
        modal = self.browser.find_elements(
            by=By.XPATH,
            value='//p[@class="mb-4 modal_subcategory"]/span'
        )
        self.assertIn('Subcategory', modal[1].text)

        # Than check Index Beneficiary Category
        modal = self.browser.find_elements(
            by=By.XPATH,
            value='//p[@class="mb-2 modal_beneficiary_category"]/span'
        )
        self.assertIn('Description', modal[1].text)

        # Than check Index Beneficiary Name
        modal = self.browser.find_elements(
            by=By.XPATH,
            value='//p[@class="mb-4 modal_beneficiary_name"]/span'
        )
        self.assertIn('Beneficiary', modal[1].text)

        # Than check Index Bank Name
        modal = self.browser.find_elements(
            by=By.XPATH,
            value='//p[@class="mb-2 modal_bank"]/span'
        )
        self.assertIn('Bank Name', modal[1].text)

        # Than check Index Bank Branch
        modal = self.browser.find_elements(
            by=By.XPATH,
            value='//p[@class="mb-2 modal_branch"]/span'
        )
        self.assertIn('1234', modal[1].text)

        # Than check Index Bank Account
        modal = self.browser.find_elements(
            by=By.XPATH,
            value='//p[@class="mb-4 modal_account"]/span'
        )
        self.assertIn('123456789', modal[1].text)

        # Than check Index Cost Center
        modal = self.browser.find_elements(
            by=By.XPATH,
            value='//p[@class="mb-2 modal_cost_center"]/span'
        )
        self.assertIn('Cost Center', modal[1].text)

        # Than check Index Cost Center Description
        modal = self.browser.find_elements(
            by=By.XPATH,
            value='//p[@class="modal_description mb-4"]/span'
        )
        self.assertIn('Description', modal[1].text)

        # Than check Index Client Name
        modal = self.browser.find_elements(
            by=By.XPATH,
            value='//p[@class="mb-4 modal_client"]/span'
        )
        self.assertIn('Client', modal[1].text)

        # Than check Index Client Country
        modal = self.browser.find_elements(
            by=By.XPATH,
            value='//p[@class="mb-2 modal_region"]/span'
        )
        self.assertIn('Country', modal[1].text)

        # Than check Index Client State
        modal = self.browser.find_elements(
            by=By.XPATH,
            value='//p[@class="mb-2 modal_state"]/span'
        )
        self.assertIn('State', modal[1].text)

        # Than check Index Client City
        modal = self.browser.find_elements(
            by=By.XPATH,
            value='//p[@class="mb-2 modal_city"]/span'
        )
        self.assertIn('City', modal[1].text)

        # User finds removal button and click on it
        self.browser.find_element(
            by=By.XPATH,
            value='//div[@id="labelRemoveModal"]/div/div/form/div/button[@type="submit"]'  # noqa: E501
        ).click()

        # An success message will display
        body = self.browser.find_element(by=By.TAG_NAME, value='body')
        self.assertIn(
            'Entry removed successfully.', body.text
        )
