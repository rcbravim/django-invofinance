import json

import pytest
from board.models import Analytic
from board.tests.test_board_helper import BoardHelperMixin
from django.db.utils import IntegrityError
from django.test import TestCase
from home.models import User
from home.tests.test_home_helper import HomeHelperMixin
from parameterized import parameterized


@pytest.mark.fast
class TestBoardAnalyticModel(TestCase, BoardHelperMixin,
                             HomeHelperMixin):
    def setUp(self) -> None:
        self.user = self.make_user()
        self.json_data = {
            'monthly': {
                'revenue': '100.00',
                'expenses': '50.00',
                'balance': '50.00',
            },
            'overall': '50.00'
        }
        self.analytic = self.make_analytic(
            user=User.objects.get(id=self.user.id),
            ana_json=self.json_data
        )
        return super().setUp()

    # checking if user_id is not null by default
    def test_analytic_if_user_id_not_null_by_default(self):
        with self.assertRaises(IntegrityError) as context:
            Analytic.objects.create(
                ana_cycle='2022-05-01',
                ana_json=json.dumps(self.json_data),
                ana_status=1
            )
        self.assertIn(
            "Column \'user_id\' cannot be null", str(context.exception)
        )

    # checking if ana_cycle is not null by default
    def test_analytic_if_ana_cycle_not_null_by_default(self):
        with self.assertRaises(IntegrityError) as context:
            Analytic.objects.create(
                user=User.objects.get(id=self.user.id),
                ana_json=json.dumps(self.json_data),
                ana_status=1
            )
        self.assertIn(
            "Column \'ana_cycle\' cannot be null", str(context.exception)
        )

    # checking if ana_json is '' (empty) by default
    def test_analytic_if_ana_json_default(self):
        analytic = Analytic.objects.create(
            user=User.objects.get(id=self.user.id),
            ana_cycle='2022-05-01',
            ana_status=1
        )
        self.assertEqual('', analytic.ana_json)

    # checking if ana_status is False by default
    def test_analytic_status_default(self):
        analytic = Analytic.objects.create(
            user=User.objects.get(id=self.user.id),
            ana_json=json.dumps(self.json_data),
            ana_cycle='2022-05-01',
        )
        self.assertFalse(analytic.ana_status)

    # checking if dates are not null by default
    @parameterized.expand([
        'ana_date_created',
        'ana_date_updated'
    ])
    def test_analytic_dates_not_null(self, field):
        self.analytic.full_clean()
        self.assertIsNotNone(
            field,
            msg=f'{field} cannot be null'
        )

    # checking if rel_date_deleted is False by default
    def test_analytic_date_deleted_default(self):
        analytic = Analytic.objects.create(
            user=User.objects.get(id=self.user.id),
            ana_json=json.dumps(self.json_data),
            ana_cycle='2022-05-01',
            ana_status=1
        )
        self.assertIsNone(analytic.ana_date_deleted)

    # checking if string representation is according to model setup
    def test_analytic_string_representation(self):
        self.analytic.full_clean()
        self.assertEqual(str(self.analytic), str(self.analytic.user))
