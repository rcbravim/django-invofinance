from unittest.mock import patch

import pytest
from board.tests.test_board_helper import BoardHelperMixin
from board.views import labels_financial_view
from django.test import TestCase
from django.urls import resolve, reverse
from home.models import User
from home.tests.test_home_helper import HomeHelperMixin
from library.utils.auth import auth
from library.utils.helper import hash_gen
from parameterized import parameterized


@pytest.mark.fast
class TestBoardViewFinancial(TestCase, HomeHelperMixin, BoardHelperMixin):
    def setUp(self) -> None:
        self.user = self.make_user(use_is_valid=True)
        self.cost_center = self.make_financial(
            user=User.objects.get(id=self.user.id),
            fin_cost_center='CostCenter',
            fin_description='Description',
            fin_type=1
        )
        self.bank_account = self.make_financial(
            user=User.objects.get(id=self.user.id),
            fin_slug=hash_gen('bank_slug'),
            fin_bank_name='BankName',
            fin_bank_branch='1234',
            fin_bank_account='123456789',
            fin_type=2
        )
        return super().setUp()

    # Testing the returned function on each view function
    def test_board_labels_financial_view_function(self):
        view = resolve(reverse('board:labels_financial'))
        self.assertIs(
            view.func.__module__,
            labels_financial_view.LabelsFinancialView.__module__
        )

    def test_board_labels_financial_edit_view_function(self):
        view = resolve(reverse('board:labels_financial_edit'))
        self.assertIs(
            view.func.__module__,
            labels_financial_view.LabelsFinancialView.__module__
        )

    def test_board_labels_financial_delete_view_function(self):
        view = resolve(reverse('board:labels_financial_delete'))
        self.assertIs(
            view.func.__module__,
            labels_financial_view.LabelsFinancialView.__module__
        )

    # Testing wich template is loaded on
    # labels_financial view function

    # without credentials
    def test_board_labels_financial_no_credentials(self):
        response = self.client.get(
            reverse('board:labels_financial'),
            follow=True
        )
        self.assertRedirects(response, reverse('home:index'), 302)
        self.assertIn('error', response.context.keys())
        self.assertNotIn('success', response.context.keys())
        self.assertEqual(
            'You are not authenticated.', response.context['error']
        )
        self.assertTemplateUsed(response, 'home/pages/index.html')

    # with credentials
    def test_board_labels_financial_with_credentials(self):
        payload = {
            'whoami': self.user.id,
            'login': self.user.use_login,
            'manager': self.user.use_is_manager
        }
        session = self.client.session
        session.update({
            'auth': auth(payload)
        })
        session.save()
        response = self.client.get(reverse('board:labels_financial'))
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('error', response.context.keys())
        self.assertNotIn('success', response.context.keys())
        self.assertIn('financial', response.context.keys())
        self.assertIn('filter', response.context.keys())
        self.assertIn('pages', response.context.keys())
        self.assertTemplateUsed(
            response, 'board/pages/labels_financial.html'
        )

    # testing pagination
    def test_board_labels_financial_pagination(self):
        self.client.post(
            reverse('home:index_auth'),
            data={
                'use_login': 'jane.doe@email.com',
                'use_password': '$Trong1234'
            },
            follow=True
        )

        for i in range(2, 100):
            self.make_financial(
                user=User.objects.get(id=self.user.id),
                fin_slug=i,
                fin_cost_center='CostCenter' + str(i),
                fin_type=1
            )

        with patch('board.views.labels_financial_view.PG_LIMIT', new=10):
            response = self.client.get(reverse('board:labels_financial'))
            self.assertEqual(
                response.context['pages']['pg_range'], [1, 2, 3, 4, 5]
            )

            response = self.client.get(
                reverse('board:labels_financial'),
                data={
                    'pg': 7
                }
            )
            self.assertEqual(
                response.context['pages']['pg_range'], [5, 6, 7, 8, 9]
            )
            self.assertEqual(response.context['pages']['total_pg'], 10)

            response = self.client.get(
                reverse('board:labels_financial'),
                data={
                    'pg': 10
                }
            )
            self.assertEqual(
                response.context['pages']['pg_range'], [6, 7, 8, 9, 10]
            )
            self.assertEqual(response.context['pages']['total_pg'], 10)

            response = self.client.get(
                reverse('board:labels_financial'),
                data={
                    'pg': 9
                }
            )
            self.assertEqual(
                response.context['pages']['pg_range'], [6, 7, 8, 9, 10]
            )
            self.assertEqual(response.context['pages']['total_pg'], 10)

    # testing filters
    def test_board_labels_financial_filters(self):
        self.client.post(
            reverse('home:index_auth'),
            data={
                'use_login': 'jane.doe@email.com',
                'use_password': '$Trong1234'
            },
            follow=True
        )

        for i in range(2, 100):
            self.make_financial(
                user=User.objects.get(id=self.user.id),
                fin_slug=i,
                fin_cost_center='CostCenter' + str(i),
                fin_type=1
            )

        with patch('board.views.labels_financial_view.PG_LIMIT', new=10):
            response = self.client.get(
                reverse('board:labels_financial'),
                data={
                    'type': 2
                }
            )

            self.assertEqual(response.context['pages']['pg_range'], [1])
            self.assertEqual(response.context['pages']['total_pg'], 1)
            self.assertEqual(len(response.context['financial']), 1)
            self.assertEqual(response.context['filter']['type'], '2')
            self.assertEqual(
                response.context['financial'][0]['fin_bank_name'],
                'BankName'
            )

            response = self.client.get(
                reverse('board:labels_financial'),
                data={
                    'search': '33'
                }
            )
            self.assertEqual(response.context['pages']['pg_range'], [1])
            self.assertEqual(response.context['pages']['total_pg'], 1)
            self.assertEqual(len(response.context['financial']), 1)
            self.assertEqual(response.context['filter']['search'], '33')
            self.assertEqual(
                response.context['financial'][0]['fin_cost_center'],
                'CostCenter33'
            )

            response = self.client.get(
                reverse('board:labels_financial'),
                data={
                    'search': 'costcenter',
                    'pg': 6
                }
            )
            self.assertEqual(
                response.context['pages']['pg_range'], [4, 5, 6, 7, 8]
            )
            self.assertEqual(response.context['pages']['total_pg'], 10)
            self.assertEqual(len(response.context['financial']), 10)
            self.assertEqual(
                response.context['filter']['search'], 'costcenter'
            )

            response = self.client.get(
                reverse('board:labels_financial'),
                data={
                    'search': 'costcenter',
                    'pg': 1
                }
            )
            self.assertEqual(
                response.context['pages']['pg_range'], [1, 2, 3, 4, 5]
            )
            self.assertEqual(response.context['pages']['total_pg'], 10)
            self.assertEqual(len(response.context['financial']), 10)
            self.assertEqual(
                response.context['filter']['search'], 'costcenter'
            )
            self.assertEqual(
                response.context['financial'][0]['fin_cost_center'],
                'CostCenter'
            )

            response = self.client.get(
                reverse('board:labels_financial'),
                data={
                    'search': 'nada'
                }
            )
            self.assertEqual(response.context['pages']['pg_range'], [])
            self.assertEqual(response.context['pages']['total_pg'], 0)
            self.assertEqual(len(response.context['financial']), 0)
            self.assertEqual(
                response.context['filter']['search'], 'nada'
            )

    # Testing editing cost center with bad data and repeated
    @parameterized.expand([
        ('CostCenter-other'),  # duplicated data
        (';;;;;'),  # invalid data
    ])
    def test_board_labels_financial_edit_cost_center_errors(self, value):
        self.client.post(
            reverse('home:index_auth'),
            data={
                'use_login': 'jane.doe@email.com',
                'use_password': '$Trong1234'
            },
            follow=True
        )

        self.make_financial(
            user=User.objects.get(id=self.user.id),
            fin_slug='other',
            fin_cost_center='CostCenter-other',
            fin_type=1
        )

        response = self.client.post(
            reverse('board:labels_financial_edit'),
            data={
                'cost_center': value,
                'edit_financial': hash_gen(self.cost_center.fin_slug)
            },
            follow=True
        )
        self.assertRedirects(
            response, reverse('board:labels_financial'), 302
        )
        self.assertIn('error', response.context.keys())
        self.assertNotIn('success', response.context.keys())
        self.assertIn('financial', response.context.keys())
        self.assertIn('filter', response.context.keys())
        self.assertIn('pages', response.context.keys())
        if value == 'CostCenter-other':
            self.assertEqual(
                'Invalid data, cost center not edited:<br />This '
                'cost center is already register in our database and cannot be used.',  # noqa: E501
                response.context['error']
            )
        else:
            self.assertEqual(
                'Invalid data, cost center not edited:<br />'
                'Entry cannot contain disallowed characters. e.g. &quot;;&quot;.',  # noqa: E501
                response.context['error']
            )
        self.assertTemplateUsed(
            response, 'board/pages/labels_financial.html'
        )

    # Testing editing cost center with good data
    def test_board_labels_financial_edit_cost_center_correctly(self):
        self.client.post(
            reverse('home:index_auth'),
            data={
                'use_login': 'jane.doe@email.com',
                'use_password': '$Trong1234'
            },
            follow=True
        )
        response = self.client.post(
            reverse('board:labels_financial_edit'),
            data={
                'cost_center': 'ValidCostCenter',
                'edit_financial': hash_gen(self.cost_center.fin_slug)
            },
            follow=True
        )
        self.assertRedirects(
            response, reverse('board:labels_financial'), 302
        )
        self.assertNotIn('error', response.context.keys())
        self.assertIn('success', response.context.keys())
        self.assertIn('financial', response.context.keys())
        self.assertIn('filter', response.context.keys())
        self.assertIn('pages', response.context.keys())
        self.assertEqual(
            'ValidCostCenter',
            response.context['financial'][1].get('fin_cost_center')
        )
        self.assertEqual(
            'Cost center edited successfully.',
            response.context['success']
        )
        self.assertTemplateUsed(
            response, 'board/pages/labels_financial.html'
        )

    # Testing editing description with bad and empty data
    def test_board_labels_financial_edit_description_bad_data(self):
        self.client.post(
            reverse('home:index_auth'),
            data={
                'use_login': 'jane.doe@email.com',
                'use_password': '$Trong1234'
            },
            follow=True
        )

        response = self.client.post(
            reverse('board:labels_financial_edit'),
            data={
                'cost_center': 'ValidCostCenter',
                'description': 'Description;;;',
                'edit_financial': hash_gen(self.cost_center.fin_slug)
            },
            follow=True
        )
        self.assertRedirects(
            response, reverse('board:labels_financial'), 302
        )
        self.assertIn('error', response.context.keys())
        self.assertNotIn('success', response.context.keys())
        self.assertIn('financial', response.context.keys())
        self.assertIn('filter', response.context.keys())
        self.assertIn('pages', response.context.keys())
        self.assertEqual(
            'Invalid data, cost center not edited:<br />'
            'Entry cannot contain disallowed characters. e.g. &quot;;&quot;.',
            response.context['error']
        )

    # Testing editing description with good data
    def test_board_labels_financial_edit_description_correctly(self):
        self.client.post(
            reverse('home:index_auth'),
            data={
                'use_login': 'jane.doe@email.com',
                'use_password': '$Trong1234'
            },
            follow=True
        )
        response = self.client.post(
            reverse('board:labels_financial_edit'),
            data={
                'cost_center': 'ValidCostCenter',
                'description': 'ValidDescription',
                'edit_financial': hash_gen(self.cost_center.fin_slug)
            },
            follow=True
        )
        self.assertRedirects(
            response, reverse('board:labels_financial'), 302
        )
        self.assertNotIn('error', response.context.keys())
        self.assertIn('success', response.context.keys())
        self.assertIn('financial', response.context.keys())
        self.assertIn('filter', response.context.keys())
        self.assertIn('pages', response.context.keys())
        self.assertEqual(
            'Cost center edited successfully.',
            response.context['success']
        )
        self.assertTemplateUsed(
            response, 'board/pages/labels_financial.html'
        )

    # Testing editing bank name with bad and empty data
    # duplicated data is not being tested here because you need to match bank,
    # account and branch
    # empty data also not being tested because bank name can be null if adding
    # cost center
    def test_board_labels_financial_edit_bank_name_bad_data(self):
        self.client.post(
            reverse('home:index_auth'),
            data={
                'use_login': 'jane.doe@email.com',
                'use_password': '$Trong1234'
            },
            follow=True
        )

        response = self.client.post(
            reverse('board:labels_financial_edit'),
            data={
                'bank': ';;;;;',
                'branch': '1234',
                'account': '123456789',
                'edit_financial': hash_gen(self.bank_account.fin_slug)
            },
            follow=True
        )
        self.assertRedirects(
            response, reverse('board:labels_financial'), 302
        )
        self.assertIn('error', response.context.keys())
        self.assertNotIn('success', response.context.keys())
        self.assertIn('financial', response.context.keys())
        self.assertIn('filter', response.context.keys())
        self.assertIn('pages', response.context.keys())
        self.assertEqual(
            'Invalid data, bank account not edited:<br />'
            'Entry cannot contain disallowed characters. e.g. &quot;;&quot;.',
            response.context['error']
        )
        self.assertTemplateUsed(
            response, 'board/pages/labels_financial.html'
        )

    # Testing editing bank name with good data
    def test_board_labels_financial_edit_bank_name_correctly(self):
        self.client.post(
            reverse('home:index_auth'),
            data={
                'use_login': 'jane.doe@email.com',
                'use_password': '$Trong1234'
            },
            follow=True
        )

        response = self.client.post(
            reverse('board:labels_financial_edit'),
            data={
                'bank': 'ValidBank',
                'branch': '1234',
                'account': '123456789',
                'edit_financial': hash_gen(self.bank_account.fin_slug)
            },
            follow=True
        )
        self.assertRedirects(
            response, reverse('board:labels_financial'), 302
        )
        self.assertNotIn('error', response.context.keys())
        self.assertIn('success', response.context.keys())
        self.assertIn('financial', response.context.keys())
        self.assertIn('filter', response.context.keys())
        self.assertIn('pages', response.context.keys())
        self.assertEqual(
            'Bank account edited successfully.',
            response.context['success']
        )
        self.assertTemplateUsed(
            response, 'board/pages/labels_financial.html'
        )

    # Testing adding branch with bad data
    @parameterized.expand([
        (';;;;;'),  # invalid data
        ('teste@'),  # only string
    ])
    def test_board_labels_financial_edit_branch_errors(self, value):
        self.client.post(
            reverse('home:index_auth'),
            data={
                'use_login': 'jane.doe@email.com',
                'use_password': '$Trong1234'
            },
            follow=True
        )
        response = self.client.post(
            reverse('board:labels_financial_edit'),
            data={
                'bank': 'ValidBank',
                'branch': value,
                'account': '123456789',
                'edit_financial': hash_gen(self.bank_account.fin_slug)
            },
            follow=True
        )
        self.assertRedirects(
            response, reverse('board:labels_financial'), 302
        )
        self.assertIn('error', response.context.keys())
        self.assertNotIn('success', response.context.keys())
        self.assertIn('financial', response.context.keys())
        self.assertIn('filter', response.context.keys())
        self.assertIn('pages', response.context.keys())
        if ';' in value:
            self.assertEqual(
                'Invalid data, bank account not edited:<br />'
                'Entry cannot contain disallowed characters. e.g. &quot;;&quot;.',  # noqa: E501
                response.context['error']
            )
        else:
            self.assertEqual(
                'Invalid data, bank account not edited:<br />'
                'Branch should must consist of numbers only.',
                response.context['error']
            )
        self.assertTemplateUsed(
            response, 'board/pages/labels_financial.html'
        )

    # Testing editing branch with good data
    def test_board_labels_financial_edit_branch_correctly(self):
        self.client.post(
            reverse('home:index_auth'),
            data={
                'use_login': 'jane.doe@email.com',
                'use_password': '$Trong1234'
            },
            follow=True
        )
        response = self.client.post(
            reverse('board:labels_financial_edit'),
            data={
                'bank': 'ValidBank',
                'branch': '1111',
                'account': '123456789',
                'edit_financial': hash_gen(self.bank_account.fin_slug)
            },
            follow=True
        )
        self.assertRedirects(
            response, reverse('board:labels_financial'), 302
        )
        self.assertNotIn('error', response.context.keys())
        self.assertIn('success', response.context.keys())
        self.assertIn('financial', response.context.keys())
        self.assertIn('filter', response.context.keys())
        self.assertIn('pages', response.context.keys())
        self.assertEqual(
            'Bank account edited successfully.',
            response.context['success']
        )
        self.assertTemplateUsed(
            response, 'board/pages/labels_financial.html'
        )

    # Testing adding account with bad data and duplicated data
    @parameterized.expand([
        ('987654321'),  # duplicated data
        (';;;;;'),  # invalid data
        ('teste@'),  # only string
    ])
    def test_board_labels_financial_edit_account_errors(self, value):
        self.client.post(
            reverse('home:index_auth'),
            data={
                'use_login': 'jane.doe@email.com',
                'use_password': '$Trong1234'
            },
            follow=True
        )
        self.make_financial(
            user=User.objects.get(id=self.user.id),
            fin_slug='other',
            fin_bank_name='BankName',
            fin_bank_branch='1234',
            fin_bank_account='987654321',
            fin_type=2
        )
        response = self.client.post(
            reverse('board:labels_financial_edit'),
            data={
                'bank': 'BankName',
                'branch': '1234',
                'account': value,
                'edit_financial': hash_gen(self.bank_account.fin_slug)
            },
            follow=True
        )
        self.assertRedirects(
            response, reverse('board:labels_financial'), 302
        )
        self.assertIn('error', response.context.keys())
        self.assertNotIn('success', response.context.keys())
        self.assertIn('financial', response.context.keys())
        self.assertIn('filter', response.context.keys())
        self.assertIn('pages', response.context.keys())
        if value == '987654321':
            self.assertEqual(
                'Invalid data, bank account not edited:<br />'
                'This bank account is already register in our database and cannot be used.',  # noqa: E501
                response.context['error']
            )
        elif ';' in value:
            self.assertEqual(
                'Invalid data, bank account not edited:<br />'
                'Entry cannot contain disallowed characters. e.g. &quot;;&quot;.',  # noqa: E501
                response.context['error']
            )
        else:
            self.assertEqual(
                'Invalid data, bank account not edited:<br />'
                'Account should must consist of numbers only.',
                response.context['error']
            )
        self.assertTemplateUsed(
            response, 'board/pages/labels_financial.html'
        )

    # Testing editing account with good data
    def test_board_labels_financial_edit_account_correctly(self):
        self.client.post(
            reverse('home:index_auth'),
            data={
                'use_login': 'jane.doe@email.com',
                'use_password': '$Trong1234'
            },
            follow=True
        )
        response = self.client.post(
            reverse('board:labels_financial_edit'),
            data={
                'bank': 'ValidBank',
                'branch': '1234',
                'account': '11111111',
                'edit_financial': hash_gen(self.bank_account.fin_slug)
            },
            follow=True
        )
        self.assertRedirects(
            response, reverse('board:labels_financial'), 302
        )
        self.assertNotIn('error', response.context.keys())
        self.assertIn('success', response.context.keys())
        self.assertIn('financial', response.context.keys())
        self.assertIn('filter', response.context.keys())
        self.assertIn('pages', response.context.keys())
        self.assertEqual(
            'Bank account edited successfully.',
            response.context['success']
        )
        self.assertTemplateUsed(
            response, 'board/pages/labels_financial.html'
        )

    # Testing deleting financial cost_center
    def test_board_labels_financial_delete_cost_center(self):
        self.client.post(
            reverse('home:index_auth'),
            data={
                'use_login': 'jane.doe@email.com',
                'use_password': '$Trong1234'
            },
            follow=True
        )
        response = self.client.post(
            reverse('board:labels_financial_delete'),
            data={
                'del_financial': hash_gen(self.cost_center.fin_slug),
            },
            follow=True
        )
        self.assertRedirects(
            response, reverse('board:labels_financial'), 302
        )
        self.assertNotIn('error', response.context.keys())
        self.assertIn('success', response.context.keys())
        self.assertIn('financial', response.context.keys())
        self.assertTrue(response.context['financial'])
        self.assertIn('filter', response.context.keys())
        self.assertIn('pages', response.context.keys())
        self.assertEqual(
            'Cost center removed successfully.',
            response.context['success']
        )
        self.assertTemplateUsed(
            response, 'board/pages/labels_financial.html'
        )

    # Testing deleting financial bank_account
    def test_board_labels_financial_delete_bank_account(self):
        self.client.post(
            reverse('home:index_auth'),
            data={
                'use_login': 'jane.doe@email.com',
                'use_password': '$Trong1234'
            },
            follow=True
        )
        response = self.client.post(
            reverse('board:labels_financial_delete'),
            data={
                'del_financial': hash_gen(self.bank_account.fin_slug),
            },
            follow=True
        )
        self.assertRedirects(
            response, reverse('board:labels_financial'), 302
        )
        self.assertNotIn('error', response.context.keys())
        self.assertIn('success', response.context.keys())
        self.assertIn('financial', response.context.keys())
        self.assertTrue(response.context['financial'])
        self.assertIn('filter', response.context.keys())
        self.assertIn('pages', response.context.keys())
        self.assertEqual(
            'Bank account removed successfully.',
            response.context['success']
        )
        self.assertTemplateUsed(
            response, 'board/pages/labels_financial.html'
        )

    # Testing deleting financial cost_center
    def test_board_labels_financial_delete_cost_center_and_bank_account(self):
        self.client.post(
            reverse('home:index_auth'),
            data={
                'use_login': 'jane.doe@email.com',
                'use_password': '$Trong1234'
            },
            follow=True
        )
        self.client.post(
            reverse('board:labels_financial_delete'),
            data={
                'del_financial': hash_gen(self.cost_center.fin_slug),
            },
            follow=True
        )
        response = self.client.post(
            reverse('board:labels_financial_delete'),
            data={
                'del_financial': hash_gen(self.bank_account.fin_slug),
            },
            follow=True
        )
        self.assertRedirects(
            response, reverse('board:labels_financial'), 302
        )
        self.assertNotIn('error', response.context.keys())
        self.assertIn('success', response.context.keys())
        self.assertIn('financial', response.context.keys())
        self.assertFalse(response.context['financial'])
        self.assertIn('filter', response.context.keys())
        self.assertIn('pages', response.context.keys())
        self.assertEqual(
            'Bank account removed successfully.',
            response.context['success']
        )
        self.assertTemplateUsed(
            response, 'board/pages/labels_financial.html'
        )
