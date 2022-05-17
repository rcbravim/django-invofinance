import pytest
from board.models import Client, Country, State
from board.tests.test_board_helper import BoardHelperMixin
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from django.test import TestCase
from home.models import User
from home.tests.test_home_helper import HomeHelperMixin
from library.utils.helper import hash_gen
from parameterized import parameterized


@pytest.mark.fast
class TestBoardClientModel(TestCase, BoardHelperMixin,
                           HomeHelperMixin):
    def setUp(self) -> None:
        self.user = self.make_user()
        self.country = self.make_country()
        self.state = self.make_state(
            country=Country.objects.get(id=self.country.id)
        )
        self.client_label = self.make_client(
            user=User.objects.get(id=self.user.id),
            country=Country.objects.get(id=self.country.id),
            state=State.objects.get(id=self.state.id),
        )
        return super().setUp()

    # checking if user_id is not null by default
    def test_client_if_user_id_not_null_by_default(self):
        with self.assertRaises(IntegrityError):
            Client.objects.create(
                cli_name='NewClient',
                cli_slug=hash_gen('hash_slug'),
                country=Country.objects.get(id=self.country.id),
                state=State.objects.get(id=self.state.id),
                cli_city='City',
                cli_status=1
            )

    # testing name max length
    def test_client_name_max_length(self):
        max = 250
        self.client_label.cli_name = ('A' * (max + 1))
        with self.assertRaises(ValidationError):
            self.client_label.full_clean()

    # checking if slug is unique according to model setup
    def test_client_slug_unique(self):
        with self.assertRaises(IntegrityError):
            self.make_client(
                user=User.objects.get(id=self.user.id),
                cli_slug=self.client_label.cli_slug,
                country=Country.objects.get(id=self.country.id),
                state=State.objects.get(id=self.state.id)
            )

    # testing slug field's max length
    def test_client_slug_max_length(self):
        max = 250
        self.client_label.cli_slug = 'A' * (max + 1)
        with self.assertRaises(ValidationError):
            self.client_label.full_clean()

    # checking if country_id is null by default
    def test_client_if_country_id_null_by_default(self):
        client_label = Client.objects.create(
            user=User.objects.get(id=self.user.id),
            cli_name='NewClient',
            cli_slug=hash_gen('hash_slug'),
            state=State.objects.get(id=self.state.id),
            cli_city='City',
            cli_status=1
        )
        self.assertIsNone(client_label.country)

    # checking if state_id is null by default
    def test_client_if_state_id_not_by_default(self):
        client_label = Client.objects.create(
            user=User.objects.get(id=self.user.id),
            cli_name='NewClient',
            cli_slug=hash_gen('hash_slug'),
            country=Country.objects.get(id=self.country.id),
            cli_city='City',
            cli_status=1
        )
        self.assertIsNone(client_label.state)

    # testing city max length
    def test_city_max_length(self):
        max = 250
        self.client_label.cli_city = 'A' * (max + 1)
        with self.assertRaises(ValidationError):
            self.client_label.full_clean()

    # sending an invalid e-mail (no @ or .)
    def test_email_if_uses_invalid_email(self):
        max = 250
        self.client_label.cli_email = 'A' * max
        with self.assertRaises(ValidationError):
            self.client_label.full_clean()

    # testing email max length
    def test_email_max_length(self):
        max = 250
        self.client_label.cli_email = ('A' * max) + '@email.com'
        with self.assertRaises(ValidationError):
            self.client_label.full_clean()

    # testing phone max length
    def test_phone_max_length(self):
        max = 20
        self.client_label.cli_phone = 'A' * (max + 1)
        with self.assertRaises(ValidationError):
            self.client_label.full_clean()

    # testing phone max length
    def test_responsible_max_length(self):
        max = 250
        self.client_label.cli_responsible = 'A' * (max + 1)
        with self.assertRaises(ValidationError):
            self.client_label.full_clean()

    # checking if cli_status is False by default
    def test_client_status_default(self):
        client_label = Client.objects.create(
            user=User.objects.get(id=self.user.id),
            cli_name='NewClient',
            cli_slug=hash_gen('hash_slug'),
            country=Country.objects.get(id=self.country.id),
            state=State.objects.get(id=self.state.id),
            cli_city='City'
        )
        self.assertFalse(client_label.cli_status)

    # checking if dates are not null by default
    @parameterized.expand([
        'cli_date_created',
        'cli_date_updated'
    ])
    def test_client_dates_not_null(self, field):
        self.client_label.full_clean()
        self.assertIsNotNone(
            field,
            msg=f'{field} cannot be null'
        )

    # checking if cli_date_deleted is False by default
    def test_clients_date_deleted_default(self):
        client_label = Client.objects.create(
            user=User.objects.get(id=self.user.id),
            cli_name='NewClient',
            cli_slug=hash_gen('hash_slug'),
            country=Country.objects.get(id=self.country.id),
            state=State.objects.get(id=self.state.id),
            cli_city='City',
            cli_status=1
        )
        self.assertIsNone(client_label.cli_date_deleted)

    # checking if string representation is according to model setup
    def test_client_string_representation(self):
        self.client_label.full_clean()
        self.assertEqual(str(self.client_label), self.client_label.cli_name)
