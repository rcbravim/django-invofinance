import pytest
from board.models import Beneficiary, BeneficiaryCategory
from board.tests.test_board_helper import BoardHelperMixin
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from django.test import TestCase
from home.models import User
from home.tests.test_home_helper import HomeHelperMixin
from parameterized import parameterized


@pytest.mark.fast
class TestBoardBeneficiaryModel(TestCase, BoardHelperMixin,
                                HomeHelperMixin):
    def setUp(self) -> None:
        self.user = self.make_user()
        self.category = self.make_beneficiary_category(
            user=User.objects.get(id=self.user.id)
        )
        self.beneficiary = self.make_beneficiary(
            user=User.objects.get(id=self.user.id),
            beneficiary_category=BeneficiaryCategory.objects.get(
                id=self.category.id
            )
        )
        return super().setUp()

    # testing name field's max length
    def test_beneficiary_name_max_length(self):
        max = 250
        self.beneficiary.ben_name = ('A' * (max + 1))
        with self.assertRaises(ValidationError):
            self.beneficiary.full_clean()

    # checking if ben_status is False by default
    def test_beneficiary_status_default(self):
        status = Beneficiary.objects.create(
            user_id=self.user.id,
            beneficiary_category=BeneficiaryCategory.objects.get(
                id=self.category.id
            ),
            ben_name='Beneficiary'
        )
        self.assertFalse(status.ben_status)

    # checking if beneficiary_category_id it cant be null
    def test_beneficiary_if_beneficiary_category_id_cant_be_null(self):
        with self.assertRaises(IntegrityError):
            Beneficiary.objects.create(
                user_id=self.user.id,
                ben_name='Beneficiary'
            )

    # checking if ben_date_deleted is null by default
    def test_beneficiary_ben_date_deleted_null_by_default(self):
        status = Beneficiary.objects.create(
            user_id=self.user.id,
            beneficiary_category=BeneficiaryCategory.objects.get(
                id=self.category.id
            ),
            ben_name='Beneficiary'
        )
        self.assertIsNone(status.ben_date_deleted)

    # checking if dates are not null by default
    @parameterized.expand([
        'ben_date_created',
        'ben_date_updated'
    ])
    def test_beneficiar_dates_not_null(self, field):
        self.beneficiary.full_clean()
        self.assertIsNotNone(
            field,
            msg=f'{field} cannot be null'
        )

    # checking if string representation is according to model setup
    def test_beneficiary_string_representation(self):
        self.beneficiary.full_clean()
        self.assertEqual(str(self.beneficiary), self.beneficiary.ben_name)

    # checking if slug is unique according to model setup
    def test_beneficiary_slug_unique(self):
        with self.assertRaises(IntegrityError):
            self.make_beneficiary(
                user=User.objects.get(id=self.user.id),
                beneficiary_category=BeneficiaryCategory.objects.get(
                    id=self.category.id
                )
            )

    # testing slug field's max length
    def test_beneficiary_slug_max_length(self):
        max = 250
        self.beneficiary.ben_slug = ('A' * (max + 1))
        with self.assertRaises(ValidationError):
            self.beneficiary.full_clean()
