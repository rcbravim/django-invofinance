import pytest
from home.models import User
from home.tests.test_home_helper import HomeHelperMixin
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from tests.functional_tests.home.test_home_base_helper import TestHelperStatic

from board.tests.test_board_helper import BoardHelperMixin


@pytest.mark.selenium
class TestBoardFinancialPage(TestHelperStatic, HomeHelperMixin,
                             BoardHelperMixin):
    """
    These tests are being created based on StaticLiveServerTestCase
    That is, with CSS and JS files
    """
    def setUp(self) -> None:
        self.user = self.make_user(use_is_valid=True)
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

        # User finds sidebar financial and click on it
        sidebar_financial = self.browser.find_element(
            by=By.XPATH, value='//a[@key="t-financial"]'
        )
        self.sleep(1)
        sidebar_financial.click()

    # Testing user login in with a existing email of a validated user
    # going to financial view details
    def test_board_financial_login_in_view_details_bank_account(self):
        self.make_financial(
            user=User.objects.get(id=self.user.id),
            fin_slug='bank_slug',
            fin_bank_name='BankName',
            fin_bank_branch='1234',
            fin_bank_account='123456789',
            fin_type=2
        )

        # Initialiazing test
        self._test_path()

        # User finds view details and click on it
        view = self.browser.find_element(
            by=By.XPATH, value='//button[@data-bs-target=".labelDetailsModal"]'
        )
        view.click()
        self.sleep(1)

        # A view description will display and user will check Bank Name
        modal = self.browser.find_element(
            by=By.XPATH,
            value='//p[@class="mb-2 modal_bank"]/span'
        )
        self.assertIn('BankName', modal.text)

        # Than check Branch Number
        modal = self.browser.find_element(
            by=By.XPATH,
            value='//p[@class="mb-2 modal_branch"]/span'
        )
        self.assertIn('1234', modal.text)

        # Than check Account Number
        modal = self.browser.find_element(
            by=By.XPATH,
            value='//p[@class="mb-2 modal_account"]/span'
        )
        self.assertIn('123456789', modal.text)

    # going to financial edit label - same data
    def test_board_financial_login_in_edit_label_same_data_bank_account(self):
        self.make_financial(
            user=User.objects.get(id=self.user.id),
            fin_slug='bank_slug',
            fin_bank_name='BankName',
            fin_bank_branch='1234',
            fin_bank_account='123456789',
            fin_type=2
        )

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
            'Bank account edited successfully.',
            body.text
        )

    # going to financial edit label - update duplicated bank_account
    def test_board_financial_login_in_edit_label_duplicated_bank_account(self):
        self.make_financial(
            user=User.objects.get(id=self.user.id),
            fin_slug='bank_slug',
            fin_bank_name='BankName',
            fin_bank_branch='1234',
            fin_bank_account='123456789',
            fin_type=2
        )

        self.make_financial(
            user=User.objects.get(id=self.user.id),
            fin_slug='bank_slug2',
            fin_bank_name='Z-Bank',
            fin_bank_branch='1234',
            fin_bank_account='123456789',
            fin_type=2
        )

        # Initialiazing test
        self._test_path()

        # User finds edit icon and click on it
        edit = self.browser.find_element(
            by=By.XPATH, value='//a[@data-bs-target=".labelEditModal"]'
        )
        edit.click()
        self.sleep(1)

        bank = self.browser.find_element(
            by=By.XPATH,
            value='//input[@id="bank"]'
        )
        bank.click()

        # User writes on input
        bank.clear()
        bank.send_keys('Z-Bank')

        # User finds button and click on it
        button = self.browser.find_element(
            by=By.XPATH,
            value='//div[@id="labelEditModal"]/div/div/form/div/button'
        )
        button.click()

        # An error message will display
        body = self.browser.find_element(by=By.TAG_NAME, value='body')
        self.assertIn(
            'This bank account is already register in our database and cannot be used.',  # noqa: E501
            body.text
        )

    # going to financial edit label - update empty bank name
    def test_board_financial_login_in_edit_label_empty_bank_name(self):
        self.make_financial(
            user=User.objects.get(id=self.user.id),
            fin_slug='bank_slug',
            fin_bank_name='BankName',
            fin_bank_branch='1234',
            fin_bank_account='123456789',
            fin_type=2
        )

        # Initialiazing test
        self._test_path()

        # User finds edit icon and click on it
        edit = self.browser.find_element(
            by=By.XPATH, value='//a[@data-bs-target=".labelEditModal"]'
        )
        edit.click()
        self.sleep(1)

        bank = self.browser.find_element(
            by=By.XPATH,
            value='//input[@id="bank"]'
        )
        bank.click()

        # User clear input
        bank.clear()

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
        self.assertIn('Please provide a bank name', modal.text)

    # going to financial edit label - update bad bank name
    def test_board_financial_login_in_edit_label_bad_bank_name(self):
        self.make_financial(
            user=User.objects.get(id=self.user.id),
            fin_slug='bank_slug',
            fin_bank_name='BankName',
            fin_bank_branch='1234',
            fin_bank_account='123456789',
            fin_type=2
        )

        # Initialiazing test
        self._test_path()

        # User finds edit icon and click on it
        edit = self.browser.find_element(
            by=By.XPATH, value='//a[@data-bs-target=".labelEditModal"]'
        )
        edit.click()
        self.sleep(1)

        bank = self.browser.find_element(
            by=By.XPATH,
            value='//input[@id="bank"]'
        )
        bank.click()

        # User writes on input
        bank.send_keys('Nada;')

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

    # going to financial edit label - update valid bank name
    def test_board_financial_login_in_edit_label_valid_bank(self):
        self.make_financial(
            user=User.objects.get(id=self.user.id),
            fin_slug='bank_slug',
            fin_bank_name='BankName',
            fin_bank_branch='1234',
            fin_bank_account='123456789',
            fin_type=2
        )

        # Initialiazing test
        self._test_path()

        # User finds edit icon and click on it
        edit = self.browser.find_element(
            by=By.XPATH, value='//a[@data-bs-target=".labelEditModal"]'
        )
        edit.click()
        self.sleep(1)

        bank = self.browser.find_element(
            by=By.XPATH,
            value='//input[@id="bank"]'
        )
        bank.click()

        # User writes on input
        bank.send_keys('Nada')

        # User finds button and click on it
        button = self.browser.find_element(
            by=By.XPATH,
            value='//div[@id="labelEditModal"]/div/div/form/div/button'
        )
        button.click()

        # A success message will display
        body = self.browser.find_element(by=By.TAG_NAME, value='body')
        self.assertIn(
            'Bank account edited successfully.',
            body.text
        )

    # going to financial edit label - update empty branch
    def test_board_financial_login_in_edit_label_empty_branch(self):
        self.make_financial(
            user=User.objects.get(id=self.user.id),
            fin_slug='bank_slug',
            fin_bank_name='BankName',
            fin_bank_branch='1234',
            fin_bank_account='123456789',
            fin_type=2
        )

        # Initialiazing test
        self._test_path()

        # User finds edit icon and click on it
        edit = self.browser.find_element(
            by=By.XPATH, value='//a[@data-bs-target=".labelEditModal"]'
        )
        edit.click()
        self.sleep(1)

        branch = self.browser.find_element(
            by=By.XPATH,
            value='//input[@id="branch"]'
        )
        branch.click()

        # User clear input
        branch.clear()

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
        self.assertIn('Please provide your bank branch number', modal.text)

    # going to financial edit label - update valid branch
    def test_board_financial_login_in_edit_label_valid_branch(self):
        self.make_financial(
            user=User.objects.get(id=self.user.id),
            fin_slug='bank_slug',
            fin_bank_name='BankName',
            fin_bank_branch='1234',
            fin_bank_account='123456789',
            fin_type=2
        )

        # Initialiazing test
        self._test_path()

        # User finds edit icon and click on it
        edit = self.browser.find_element(
            by=By.XPATH, value='//a[@data-bs-target=".labelEditModal"]'
        )
        edit.click()
        self.sleep(1)

        branch = self.browser.find_element(
            by=By.XPATH,
            value='//input[@id="branch"]'
        )
        branch.click()

        # User writes on input
        branch.clear()
        branch.send_keys('1234567888')

        # User finds button and click on it
        button = self.browser.find_element(
            by=By.XPATH,
            value='//div[@id="labelEditModal"]/div/div/form/div/button'
        )
        button.click()

        # A success message will display
        body = self.browser.find_element(by=By.TAG_NAME, value='body')
        self.assertIn(
            'Bank account edited successfully.',
            body.text
        )

    # going to financial edit label - update empty account
    def test_board_financial_login_in_edit_label_empty_account(self):
        self.make_financial(
            user=User.objects.get(id=self.user.id),
            fin_slug='bank_slug',
            fin_bank_name='BankName',
            fin_bank_branch='1234',
            fin_bank_account='123456789',
            fin_type=2
        )

        # Initialiazing test
        self._test_path()

        # User finds edit icon and click on it
        edit = self.browser.find_element(
            by=By.XPATH, value='//a[@data-bs-target=".labelEditModal"]'
        )
        edit.click()
        self.sleep(1)

        account = self.browser.find_element(
            by=By.XPATH,
            value='//input[@id="account"]'
        )
        account.click()

        # User clear input
        account.clear()

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
        self.assertIn('Please provide your account number', modal.text)

    # going to financial edit label - update valid account
    def test_board_financial_login_in_edit_label_valid_account(self):
        self.make_financial(
            user=User.objects.get(id=self.user.id),
            fin_slug='bank_slug',
            fin_bank_name='BankName',
            fin_bank_branch='1234',
            fin_bank_account='123456789',
            fin_type=2
        )

        # Initialiazing test
        self._test_path()

        # User finds edit icon and click on it
        edit = self.browser.find_element(
            by=By.XPATH, value='//a[@data-bs-target=".labelEditModal"]'
        )
        edit.click()
        self.sleep(1)

        account = self.browser.find_element(
            by=By.XPATH,
            value='//input[@id="account"]'
        )
        account.click()

        # User writes on input
        account.clear()
        account.send_keys('1234567888')

        # User finds button and click on it
        button = self.browser.find_element(
            by=By.XPATH,
            value='//div[@id="labelEditModal"]/div/div/form/div/button'
        )
        button.click()

        # A success message will display
        body = self.browser.find_element(by=By.TAG_NAME, value='body')
        self.assertIn(
            'Bank account edited successfully.',
            body.text
        )

    # Testing user login in with a existing email of a validated user
    # going to financial view details
    def test_board_financial_login_in_view_details_cost_center(self):
        self.make_financial(
            user=User.objects.get(id=self.user.id),
            fin_cost_center='CostCenter',
            fin_description='Description',
            fin_type=1
        )

        # Initialiazing test
        self._test_path()

        # User finds view details and click on it
        view = self.browser.find_element(
            by=By.XPATH, value='//button[@data-bs-target=".labelDetailsModal"]'
        )
        view.click()
        self.sleep(1)

        # A view description will display and user will check Cost Center
        modal = self.browser.find_element(
            by=By.XPATH,
            value='//p[@class="mb-2 modal_cost_center"]/span'
        )
        self.assertIn('CostCenter', modal.text)

        # Than check Description
        modal = self.browser.find_element(
            by=By.XPATH,
            value='//p[@class="mb-2 modal_description"]/span'
        )
        self.assertIn('Description', modal.text)

    # going to financial edit label - same data
    def test_board_financial_login_in_edit_label_same_data_cost_center(self):
        self.make_financial(
            user=User.objects.get(id=self.user.id),
            fin_cost_center='CostCenter',
            fin_description='Description',
            fin_type=1
        )

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
            'Cost center edited successfully.',
            body.text
        )

    # going to financial edit label - update duplicated cost center
    def test_board_financial_login_in_edit_label_duplicated_cost_center(self):
        self.make_financial(
            user=User.objects.get(id=self.user.id),
            fin_cost_center='CostCenter',
            fin_description='Description',
            fin_type=1
        )

        self.make_financial(
            user=User.objects.get(id=self.user.id),
            fin_slug='costcenterslug',
            fin_cost_center='Z-CostCenter',
            fin_description='Description',
            fin_type=1
        )

        # Initialiazing test
        self._test_path()

        # User finds edit icon and click on it
        edit = self.browser.find_element(
            by=By.XPATH, value='//a[@data-bs-target=".labelEditModal"]'
        )
        edit.click()
        self.sleep(1)

        cost_center = self.browser.find_element(
            by=By.XPATH,
            value='//input[@id="cost_center"]'
        )
        cost_center.click()

        # User writes on input
        cost_center.clear()
        cost_center.send_keys('Z-CostCenter')

        # User finds button and click on it
        button = self.browser.find_element(
            by=By.XPATH,
            value='//div[@id="labelEditModal"]/div/div/form/div/button'
        )
        button.click()

        # An error message will display
        body = self.browser.find_element(by=By.TAG_NAME, value='body')
        self.assertIn(
            'This cost center is already register in our database and cannot be used.',  # noqa: E501
            body.text
        )

    # going to financial edit label - update empty cost center
    def test_board_financial_login_in_edit_label_empty_cost_center(self):
        self.make_financial(
            user=User.objects.get(id=self.user.id),
            fin_cost_center='CostCenter',
            fin_description='Description',
            fin_type=1
        )

        # Initialiazing test
        self._test_path()

        # User finds edit icon and click on it
        edit = self.browser.find_element(
            by=By.XPATH, value='//a[@data-bs-target=".labelEditModal"]'
        )
        edit.click()
        self.sleep(1)

        cost_center = self.browser.find_element(
            by=By.XPATH,
            value='//input[@id="cost_center"]'
        )
        cost_center.click()

        # User clear input
        cost_center.clear()

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
        self.assertIn('Please provide a cost center name', modal.text)

    # going to financial edit label - update bad cost center
    def test_board_financial_login_in_edit_label_bad_cost_center(self):
        self.make_financial(
            user=User.objects.get(id=self.user.id),
            fin_cost_center='CostCenter',
            fin_description='Description',
            fin_type=1
        )

        # Initialiazing test
        self._test_path()

        # User finds edit icon and click on it
        edit = self.browser.find_element(
            by=By.XPATH, value='//a[@data-bs-target=".labelEditModal"]'
        )
        edit.click()
        self.sleep(1)

        cost_center = self.browser.find_element(
            by=By.XPATH,
            value='//input[@id="cost_center"]'
        )
        cost_center.click()

        # User clear input
        cost_center.send_keys('Nada;')

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

    # going to financial edit label - update valid cost center
    def test_board_financial_login_in_edit_label_valid_cost_center(self):
        self.make_financial(
            user=User.objects.get(id=self.user.id),
            fin_cost_center='CostCenter',
            fin_description='Description',
            fin_type=1
        )

        # Initialiazing test
        self._test_path()

        # User finds edit icon and click on it
        edit = self.browser.find_element(
            by=By.XPATH, value='//a[@data-bs-target=".labelEditModal"]'
        )
        edit.click()
        self.sleep(1)

        cost_center = self.browser.find_element(
            by=By.XPATH,
            value='//input[@id="cost_center"]'
        )
        cost_center.click()

        # User writes on input
        cost_center.send_keys('Nada')

        # User finds button and click on it
        button = self.browser.find_element(
            by=By.XPATH,
            value='//div[@id="labelEditModal"]/div/div/form/div/button'
        )
        button.click()

        # A success message will display
        body = self.browser.find_element(by=By.TAG_NAME, value='body')
        self.assertIn(
            'Cost center edited successfully.',
            body.text
        )

    # going to financial edit label - update bad description
    def test_board_financial_login_in_edit_label_bad_description(self):
        self.make_financial(
            user=User.objects.get(id=self.user.id),
            fin_cost_center='CostCenter',
            fin_description='Description',
            fin_type=1
        )

        # Initialiazing test
        self._test_path()

        # User finds edit icon and click on it
        edit = self.browser.find_element(
            by=By.XPATH, value='//a[@data-bs-target=".labelEditModal"]'
        )
        edit.click()
        self.sleep(1)

        description = self.browser.find_element(
            by=By.XPATH,
            value='//input[@id="description"]'
        )
        description.click()

        # User clear input
        description.send_keys('Nada;')

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

    # going to financial edit label - update valid description
    def test_board_financial_login_in_edit_label_valid_description(self):
        self.make_financial(
            user=User.objects.get(id=self.user.id),
            fin_cost_center='CostCenter',
            fin_description='Description',
            fin_type=1
        )

        # Initialiazing test
        self._test_path()

        # User finds edit icon and click on it
        edit = self.browser.find_element(
            by=By.XPATH, value='//a[@data-bs-target=".labelEditModal"]'
        )
        edit.click()
        self.sleep(1)

        description = self.browser.find_element(
            by=By.XPATH,
            value='//input[@id="description"]'
        )
        description.click()

        # User writes on input
        description.send_keys('Nada')

        # User finds button and click on it
        button = self.browser.find_element(
            by=By.XPATH,
            value='//div[@id="labelEditModal"]/div/div/form/div/button'
        )
        button.click()

        # A success message will display
        body = self.browser.find_element(by=By.TAG_NAME, value='body')
        self.assertIn(
            'Cost center edited successfully.',
            body.text
        )
