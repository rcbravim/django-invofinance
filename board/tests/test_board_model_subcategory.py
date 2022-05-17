import pytest
from board.models import Category, SubCategory
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
        self.subcategory = self.make_subcategory(
            category=Category.objects.get(id=self.category.id)
        )
        return super().setUp()

    # testing name field's max length
    def test_subcategory_name_max_length(self):
        max = 250
        self.subcategory.sub_name = ('A' * (max + 1))
        with self.assertRaises(ValidationError):
            self.subcategory.full_clean()

    # checking if cat_status is False by default
    def test_subcategory_status_default(self):
        status = SubCategory.objects.create(
            category=Category.objects.get(id=self.category.id),
            sub_name='CategoryName',
        )
        self.assertFalse(status.sub_status)

    # checking if category_id is not null by default
    def test_subcategory_if_category_id_not_null_by_default(self):
        with self.assertRaises(IntegrityError):
            SubCategory.objects.create(
                sub_name='Description'
            )

    # checking if sub_date_deleted is False by default
    def test_subcategory_date_deleted_default(self):
        status = SubCategory.objects.create(
            category=Category.objects.get(id=self.category.id),
            sub_name='Description'
        )
        self.assertIsNone(status.sub_date_deleted)

    # checking if dates are not null by default
    @parameterized.expand([
        'sub_date_created',
        'sub_date_updated'
    ])
    def test_subcategory_dates_not_null(self, field):
        self.subcategory.full_clean()
        self.assertIsNotNone(
            field,
            msg=f'{field} cannot be null'
        )

    # checking if string representation is according to model setup
    def test_subcategory_string_representation(self):
        self.subcategory.full_clean()
        self.assertEqual(str(self.subcategory), self.subcategory.sub_name)

    # checking if slug is unique according to model setup
    def test_subcategory_slug_unique(self):
        with self.assertRaises(IntegrityError):
            self.make_subcategory(
                category=Category.objects.get(id=self.category.id),
                sub_name='Description',
                sub_slug=self.subcategory.sub_slug
            )

    # testing slug field's max length
    def test_subcategory_slug_max_length(self):
        max = 250
        self.subcategory.sub_slug = ('A' * (max + 1))
        with self.assertRaises(ValidationError):
            self.subcategory.full_clean()
