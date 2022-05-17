import pytest
from board.models import (Beneficiary, BeneficiaryCategory, Category, Client,
                          Country, Financial, Release, State, SubCategory)
from board.tests.test_board_helper import BoardHelperMixin
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from django.test import TestCase
from home.models import User
from home.tests.test_home_helper import HomeHelperMixin
from library.utils.helper import hash_gen
from parameterized import parameterized


@pytest.mark.fast
class TestBoardReleaseModel(TestCase, BoardHelperMixin,
                            HomeHelperMixin):
    def setUp(self) -> None:
        self.user = self.make_user()
        self.category = self.make_category(
            user=User.objects.get(id=self.user.id),
        )
        self.subcategory = self.make_subcategory(
            category=Category.objects.get(id=self.category.id)
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
        self.entry = self.make_release(
            user=User.objects.get(id=self.user.id),
            subcategory=SubCategory.objects.get(id=self.subcategory.id),
            beneficiary=Beneficiary.objects.get(id=self.beneficiary.id),
            client=Client.objects.get(id=self.client_label.id),
            financial_cost_center=Financial.objects.get(id=self.cost_center.id),  # noqa: E501
            financial_account=Financial.objects.get(id=self.bank_account.id),
        )
        return super().setUp()

    # checking if user_id is not null by default
    def test_release_if_user_id_not_null_by_default(self):
        with self.assertRaises(IntegrityError) as context:
            Release.objects.create(
                rel_slug=hash_gen('hash_slug'),
                rel_gen_status=1,
                rel_entry_date='2022-05-16',
                rel_amount=1000.00,
                rel_monthly_balance=1000.00,
                rel_overall_balance=1000.00,
                rel_sqn=1,
                rel_status=1
            )
        self.assertIn(
            "Column 'user_id' cannot be null", str(context.exception)
        )

    # checking if slug is unique according to model setup
    def test_release_slug_unique(self):
        with self.assertRaises(IntegrityError) as context:
            self.make_release(
                user=User.objects.get(id=self.user.id),
                rel_slug=self.entry.rel_slug
            )
        self.assertIn(
            "Duplicate entry \'slug\' for key \'rel_slug\'",
            str(context.exception)
        )

    # testing slug field's max length
    def test_release_slug_max_length(self):
        max = 250
        self.entry.rel_slug = 'A' * (max + 1)
        with self.assertRaises(ValidationError):
            self.entry.full_clean()

    # checking if gen_status is not null by default
    def test_release_if_gen_status_not_null_by_default(self):
        with self.assertRaises(IntegrityError) as context:
            Release.objects.create(
                user=User.objects.get(id=self.user.id),
                rel_slug=hash_gen('hash_slug'),
                rel_entry_date='2022-05-16',
                rel_amount=1000.00,
                rel_monthly_balance=1000.00,
                rel_overall_balance=1000.00,
                rel_sqn=1,
                rel_status=1
            )
        self.assertIn(
            "Column \'rel_gen_status\' cannot be null", str(context.exception)
        )

    # checking if entry_date is not null by default
    def test_release_if_entry_date_not_null_by_default(self):
        with self.assertRaises(IntegrityError) as context:
            Release.objects.create(
                user=User.objects.get(id=self.user.id),
                rel_slug=hash_gen('hash_slug'),
                rel_gen_status=1,
                rel_amount=1000.00,
                rel_monthly_balance=1000.00,
                rel_overall_balance=1000.00,
                rel_sqn=1,
                rel_status=1
            )
        self.assertIn(
            "Column \'rel_entry_date\' cannot be null", str(context.exception)
        )

    # checking if amount is not null by default
    def test_release_if_amount_not_null_by_default(self):
        with self.assertRaises(IntegrityError) as context:
            Release.objects.create(
                user=User.objects.get(id=self.user.id),
                rel_slug=hash_gen('hash_slug'),
                rel_entry_date='2022-05-16',
                rel_gen_status=1,
                rel_monthly_balance=1000.00,
                rel_overall_balance=1000.00,
                rel_sqn=1,
                rel_status=1
            )
        self.assertIn(
            "Column \'rel_amount\' cannot be null", str(context.exception)
        )

    # checking if monthly_balance is not null by default
    def test_release_if_monthly_balance_not_null_by_default(self):
        with self.assertRaises(IntegrityError) as context:
            Release.objects.create(
                user=User.objects.get(id=self.user.id),
                rel_slug=hash_gen('hash_slug'),
                rel_entry_date='2022-05-16',
                rel_gen_status=1,
                rel_amount=1000.00,
                rel_overall_balance=1000.00,
                rel_sqn=1,
                rel_status=1
            )
        self.assertIn(
            "Column \'rel_monthly_balance\' cannot be null",
            str(context.exception)
        )

    # checking if overall_balance is not null by default
    def test_release_if_overall_balance_not_null_by_default(self):
        with self.assertRaises(IntegrityError) as context:
            Release.objects.create(
                user=User.objects.get(id=self.user.id),
                rel_slug=hash_gen('hash_slug'),
                rel_entry_date='2022-05-16',
                rel_gen_status=1,
                rel_amount=1000.00,
                rel_monthly_balance=1000.00,
                rel_sqn=1,
                rel_status=1
            )
        self.assertIn(
            "Column \'rel_overall_balance\' cannot be null",
            str(context.exception)
        )

    # testing description max length
    def test_release_description_max_length(self):
        max = 250
        self.entry.rel_description = ('A' * (max + 1))
        with self.assertRaises(ValidationError):
            self.entry.full_clean()

    # checking if subcategory_id is null by default
    def test_release_if_subcategory_id_null_by_default(self):
        entry = Release.objects.create(
            user=User.objects.get(id=self.user.id),
            rel_slug=hash_gen('hash_slug'),
            rel_entry_date='2022-05-16',
            rel_gen_status=1,
            rel_amount=1000.00,
            rel_monthly_balance=1000.00,
            rel_overall_balance=1000.00,
            rel_sqn=1,
            rel_status=1
        )
        self.assertIsNone(entry.subcategory)

    # checking if beneficiary_id is null by default
    def test_release_if_beneficiary_id_null_by_default(self):
        entry = Release.objects.create(
            user=User.objects.get(id=self.user.id),
            rel_slug=hash_gen('hash_slug'),
            rel_entry_date='2022-05-16',
            rel_gen_status=1,
            rel_amount=1000.00,
            rel_monthly_balance=1000.00,
            rel_overall_balance=1000.00,
            rel_sqn=1,
            rel_status=1
        )
        self.assertIsNone(entry.beneficiary)

    # checking if client_id is null by default
    def test_release_if_client_id_null_by_default(self):
        entry = Release.objects.create(
            user=User.objects.get(id=self.user.id),
            rel_slug=hash_gen('hash_slug'),
            rel_entry_date='2022-05-16',
            rel_gen_status=1,
            rel_amount=1000.00,
            rel_monthly_balance=1000.00,
            rel_overall_balance=1000.00,
            rel_sqn=1,
            rel_status=1
        )
        self.assertIsNone(entry.client)

    # checking if financial_cost_center_id is null by default
    def test_release_if_financial_cost_center_id_null_by_default(self):
        entry = Release.objects.create(
            user=User.objects.get(id=self.user.id),
            rel_slug=hash_gen('hash_slug'),
            rel_entry_date='2022-05-16',
            rel_gen_status=1,
            rel_amount=1000.00,
            rel_monthly_balance=1000.00,
            rel_overall_balance=1000.00,
            rel_sqn=1,
            rel_status=1
        )
        self.assertIsNone(entry.financial_cost_center)

    # checking if financial_account_id is null by default
    def test_release_if_financial_account_id_null_by_default(self):
        entry = Release.objects.create(
            user=User.objects.get(id=self.user.id),
            rel_slug=hash_gen('hash_slug'),
            rel_entry_date='2022-05-16',
            rel_gen_status=1,
            rel_amount=1000.00,
            rel_monthly_balance=1000.00,
            rel_overall_balance=1000.00,
            rel_sqn=1,
            rel_status=1
        )
        self.assertIsNone(entry.financial_account)

    # checking if overall_balance is not null by default
    def test_release_if_sqn_not_null_by_default(self):
        with self.assertRaises(IntegrityError) as context:
            Release.objects.create(
                user=User.objects.get(id=self.user.id),
                rel_slug=hash_gen('hash_slug'),
                rel_entry_date='2022-05-16',
                rel_gen_status=1,
                rel_amount=1000.00,
                rel_monthly_balance=1000.00,
                rel_overall_balance=1000.00,
                rel_status=1
            )
        self.assertIn(
            "Column \'rel_sqn\' cannot be null",
            str(context.exception)
        )

    # checking if rel_status is False by default
    def test_release_status_default(self):
        entry = Release.objects.create(
            user=User.objects.get(id=self.user.id),
            rel_slug=hash_gen('hash_slug'),
            rel_entry_date='2022-05-16',
            rel_gen_status=1,
            rel_amount=1000.00,
            rel_monthly_balance=1000.00,
            rel_overall_balance=1000.00,
            rel_sqn=1,
        )
        self.assertFalse(entry.rel_status)

    # checking if dates are not null by default
    @parameterized.expand([
        'rel_date_created',
        'rel_date_updated'
    ])
    def test_release_dates_not_null(self, field):
        self.client_label.full_clean()
        self.assertIsNotNone(
            field,
            msg=f'{field} cannot be null'
        )

    # checking if rel_date_deleted is False by default
    def test_release_date_deleted_default(self):
        entry = Release.objects.create(
            user=User.objects.get(id=self.user.id),
            rel_slug=hash_gen('hash_slug'),
            rel_entry_date='2022-05-16',
            rel_gen_status=1,
            rel_amount=1000.00,
            rel_monthly_balance=1000.00,
            rel_overall_balance=1000.00,
            rel_sqn=1,
            rel_status=1
        )
        self.assertIsNone(entry.rel_date_deleted)

    # checking if string representation is according to model setup
    def test_release_string_representation(self):
        self.entry.full_clean()
        self.assertEqual(str(self.entry), str(self.entry.user))
