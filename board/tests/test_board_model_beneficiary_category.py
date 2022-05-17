import pytest
from board.models import BeneficiaryCategory
from board.tests.test_board_helper import BoardHelperMixin
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from django.test import TestCase
from home.models import User
from home.tests.test_home_helper import HomeHelperMixin
from parameterized import parameterized


@pytest.mark.fast
class TestBoardBeneficiaryCategoryModel(TestCase, BoardHelperMixin,
                                        HomeHelperMixin):
    def setUp(self) -> None:
        self.user = self.make_user()
        self.category = self.make_beneficiary_category(
            user=User.objects.get(id=self.user.id)
        )
        return super().setUp()

    # testing description field's max length
    def test_beneficiary_category_description_max_length(self):
        max = 250
        self.category.cat_description = ('A' * (max + 1))
        with self.assertRaises(ValidationError):
            self.category.full_clean()

    # checking if cat_status is False by default
    def test_beneficiary_category_status_default(self):
        status = BeneficiaryCategory.objects.create(
            cat_description='Description'
        )
        self.assertFalse(status.cat_status)

    # checking if user_id is null by default
    def test_beneficiary_category_if_user_id_null_by_default(self):
        status = BeneficiaryCategory.objects.create(
            cat_description='Description'
        )
        self.assertIsNone(status.user)

    # checking if cat_date_deleted is False by default
    def test_beneficiary_category_date_deleted_default(self):
        status = BeneficiaryCategory.objects.create(
            cat_description='Description'
        )
        self.assertIsNone(status.cat_date_deleted)

    # checking if dates are not null by default
    @parameterized.expand([
        'cat_date_created',
        'cat_date_updated'
    ])
    def test_beneficiary_category_dates_not_null(self, field):
        self.category.full_clean()
        self.assertIsNotNone(
            field,
            msg=f'{field} cannot be null'
        )

    # checking if string representation is according to model setup
    def test_beneficiary_category_string_representation(self):
        self.category.full_clean()
        self.assertEqual(str(self.category), self.category.cat_description)

    # checking if slug is unique according to model setup
    def test_beneficiary_category_slug_unique(self):
        with self.assertRaises(IntegrityError):
            self.make_beneficiary_category(
                user=User.objects.get(id=self.user.id),
                cat_slug=self.category.cat_slug
            )

    # testing slug field's max length
    def test_beneficiary_category_slug_max_length(self):
        max = 250
        self.category.cat_slug = ('A' * (max + 1))
        with self.assertRaises(ValidationError):
            self.category.full_clean()
