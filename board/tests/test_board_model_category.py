import pytest
from board.models import Category
from board.tests.test_board_helper import BoardHelperMixin
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from django.test import TestCase
from home.models import User
from home.tests.test_home_helper import HomeHelperMixin
from parameterized import parameterized


@pytest.mark.fast
class TestBoardCategoryModel(TestCase, BoardHelperMixin,
                             HomeHelperMixin):
    def setUp(self) -> None:
        self.user = self.make_user()
        self.category = self.make_category(
            user=User.objects.get(id=self.user.id)
        )
        return super().setUp()

    # testing name field's max length
    def test_category_name_max_length(self):
        max = 250
        self.category.cat_name = ('A' * (max + 1))
        with self.assertRaises(ValidationError):
            self.category.full_clean()

    # checking if cat_status is False by default
    def test_category_status_default(self):
        status = Category.objects.create(
            user=User.objects.get(id=self.user.id),
            cat_name='CategoryName',
            cat_type=1
        )
        self.assertFalse(status.cat_status)

    # checking if user_id is not null by default
    def test_category_if_user_id_not_null_by_default(self):
        with self.assertRaises(IntegrityError):
            Category.objects.create(
                cat_name='Description',
                cat_type=1
            )

    # checking if cat_type is not null by default
    def test_category_if_type_not_null_by_default(self):
        with self.assertRaises(IntegrityError):
            Category.objects.create(
                user=User.objects.get(id=self.user.id),
                cat_name='Description'
            )

    # checking if cat_date_deleted is False by default
    def test_category_date_deleted_default(self):
        status = Category.objects.create(
            user=User.objects.get(id=self.user.id),
            cat_name='CategoryName',
            cat_type=1
        )
        self.assertIsNone(status.cat_date_deleted)

    # checking if dates are not null by default
    @parameterized.expand([
        'cat_date_created',
        'cat_date_updated'
    ])
    def test_category_dates_not_null(self, field):
        self.category.full_clean()
        self.assertIsNotNone(
            field,
            msg=f'{field} cannot be null'
        )

    # checking if string representation is according to model setup
    def test_category_string_representation(self):
        self.category.full_clean()
        self.assertEqual(str(self.category), self.category.cat_name)

    # checking if slug is unique according to model setup
    def test_category_slug_unique(self):
        with self.assertRaises(IntegrityError):
            self.make_category(
                user=User.objects.get(id=self.user.id),
                cat_slug=self.category.cat_slug
            )

    # testing slug field's max length
    def test_category_slug_max_length(self):
        max = 250
        self.category.cat_slug = ('A' * (max + 1))
        with self.assertRaises(ValidationError):
            self.category.full_clean()
