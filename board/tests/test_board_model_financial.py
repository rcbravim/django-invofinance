import pytest
from board.models import Financial
from board.tests.test_board_helper import BoardHelperMixin
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from django.test import TestCase
from home.models import User
from home.tests.test_home_helper import HomeHelperMixin
from library.utils.helper import hash_gen
from parameterized import parameterized


@pytest.mark.fast
class TestBoardFinancialModel(TestCase, BoardHelperMixin,
                              HomeHelperMixin):
    def setUp(self) -> None:
        self.user = self.make_user()
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
        return super().setUp()

    # checking if user_id is not null by default
    def test_financial_if_user_id_not_null_by_default(self):
        with self.assertRaises(IntegrityError):
            Financial.objects.create(
                fin_slug=hash_gen('hash_slug'),
                fin_type=1,
                fin_status=True
            )

    # checking if slug is unique according to model setup
    def test_financial_slug_unique(self):
        with self.assertRaises(IntegrityError):
            self.make_financial(
                user=User.objects.get(id=self.user.id),
                fin_slug='slug',
                fin_type=1,
                fin_status=True
            )

    # testing slug field's max length
    def test_financial_slug_max_length(self):
        max = 250
        self.cost_center.fin_slug = 'A' * (max + 1)
        with self.assertRaises(ValidationError):
            self.cost_center.full_clean()

    # testing cost_center max length
    def test_financial_cost_center_max_length(self):
        max = 250
        self.cost_center.fin_cost_center = ('A' * (max + 1))
        with self.assertRaises(ValidationError):
            self.cost_center.full_clean()

    # testing description max length
    def test_financial_description_max_length(self):
        max = 250
        self.cost_center.fin_description = ('A' * (max + 1))
        with self.assertRaises(ValidationError):
            self.cost_center.full_clean()

    # testing bank_name max length
    def test_financial_bank_name_max_length(self):
        max = 250
        self.bank_account.fin_bank_name = ('A' * (max + 1))
        with self.assertRaises(ValidationError):
            self.bank_account.full_clean()

    # testing bank_branch max length
    def test_financial_bank_branch_max_length(self):
        max = 20
        self.bank_account.fin_bank_branch = ('0' * (max + 1))
        with self.assertRaises(ValidationError):
            self.bank_account.full_clean()

    # testing bank_account max length
    def test_financial_bank_account_max_length(self):
        max = 20
        self.bank_account.fin_bank_account = ('0' * (max + 1))
        with self.assertRaises(ValidationError):
            self.bank_account.full_clean()

    # checking if variables are null by default
    def test_financial_if_variables_are_null_by_default(self):
        financial = self.make_financial(
            user=User.objects.get(id=self.user.id),
            fin_slug='slug-other',
            fin_type=1,
            fin_status=True
        )
        self.assertIsNone(financial.fin_cost_center)
        self.assertIsNone(financial.fin_description)
        self.assertIsNone(financial.fin_bank_name)
        self.assertIsNone(financial.fin_bank_branch)
        self.assertIsNone(financial.fin_bank_account)

    # checking if fin_status is False by default
    def test_financial_status_default(self):
        financial = Financial.objects.create(
            user=User.objects.get(id=self.user.id),
            fin_slug='slug-other',
            fin_type=1,
        )
        self.assertFalse(financial.fin_status)

    # checking if dates are not null by default
    @parameterized.expand([
        'fin_date_created',
        'fin_date_updated'
    ])
    def test_financial_dates_not_null(self, field):
        self.cost_center.full_clean()
        self.assertIsNotNone(
            field,
            msg=f'{field} cannot be null'
        )

    # checking if fin_date_deleted is False by default
    def test_financial_date_deleted_default(self):
        financial = Financial.objects.create(
            user=User.objects.get(id=self.user.id),
            fin_slug='slug-other',
            fin_type=1,
            fin_status=True
        )
        self.assertIsNone(financial.fin_date_deleted)

    # checking if string representation is according to model setup
    def test_financial_string_representation(self):
        # Type == 1
        self.cost_center.full_clean()
        self.assertEqual(str(self.cost_center), self.cost_center.fin_cost_center)  # noqa: E501

        # Type == 2
        self.bank_account.full_clean()
        self.assertEqual(str(self.bank_account), self.bank_account.fin_bank_name)  # noqa: E501
