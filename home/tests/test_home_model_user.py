import pytest
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from django.test import TestCase
from home.models import User
from home.tests.test_home_helper import HomeHelperMixin
from library.utils.helper import hash_gen
# o pytest faz a parametrização sem a necessidade de instalar o parameterized ?
from parameterized import parameterized


@pytest.mark.fast
class TestHomeUserModel(TestCase, HomeHelperMixin):
    def setUp(self) -> None:
        self.user = self.make_user()
        return super().setUp()

    # creating an invalid e-mail (no @ or .)
    def test_user_login_if_uses_invalid_email(self):
        max = 250
        self.user.use_login = ('A' * max)
        with self.assertRaises(ValidationError):
            self.user.full_clean()

    # testing field's max length setup with parameterized
    @parameterized.expand([
        ('use_login', 250),
        ('use_password', 128)
    ])
    def test_user_max_length(self, field, max):
        if 'use_login' in field:
            setattr(self.user, field, ('A' * max) + '@email.com')
        else:
            setattr(self.user, field, ('A' * (max + 1)))
        with self.assertRaises(ValidationError):
            self.user.full_clean()

    # checking if use_status is False by default
    def test_user_status_default(self):
        status = User.objects.create(
            use_login='jane.doe@email.com',
            use_password=hash_gen('test')
        )
        self.assertFalse(
            status.use_status,
            msg='use_status is not false by default'
        )

    # checking if use_is_valid is False by default
    def test_user_is_valid_default(self):
        status = User.objects.create(
            use_login='jane.doe@email.com',
            use_password=hash_gen('test')
        )
        self.assertFalse(
            status.use_is_valid,
            msg='use_is_valid is not false by default'
        )

    # checking if use_is_manager is False by default
    def test_user_is_manager_default(self):
        status = User.objects.create(
            use_login='jane.doe@email.com',
            use_password=hash_gen('test')
        )
        self.assertFalse(
            status.use_is_manager,
            msg='use_is_manager is not false by default'
        )

    # checking if use_date_deleted is False by default
    def test_user_date_deleted_default(self):
        status = User.objects.create(
            use_login='jane.doe@email.com',
            use_password=hash_gen('test')
        )
        self.assertFalse(
            status.use_date_deleted,
            msg='use_date_deleted is not false by default'
        )

    # checking if dates are not null by default
    @parameterized.expand([
        'use_date_created',
        'use_date_updated'
    ])
    def test_user_dates_not_null(self, field):
        self.user.full_clean()
        self.assertIsNotNone(
            field,
            msg=f'{field} cannot be null'
        )

    # checking if string representation is according to model setup
    def test_user_string_representation(self):
        self.user.full_clean()
        self.assertEqual(
            str(self.user),
            self.user.use_login,
            msg='string representantion not showing desirable value'
        )
