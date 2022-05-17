from datetime import datetime, timedelta
from unittest.mock import patch

import pytest
from board.models import (Beneficiary, BeneficiaryCategory, Category, Client,
                          Country, Financial, State, SubCategory)
from board.tests.test_board_helper import BoardHelperMixin
from board.views import index_view
from django.test import TestCase
from django.urls import resolve, reverse
from home.models import User
from home.tests.test_home_helper import HomeHelperMixin
from library.utils.auth import auth
from library.utils.helper import hash_gen
from parameterized import parameterized


@pytest.mark.fast
class TestBoardViewIndex(TestCase, BoardHelperMixin, HomeHelperMixin):
    def setUp(self) -> None:
        self.user = self.make_user(use_is_valid=True)
        self.category_income = self.make_category(
            user=User.objects.get(id=self.user.id),
        )
        self.category_expense = self.make_category(
            user=User.objects.get(id=self.user.id),
            cat_slug='slug_expense',
            cat_type=2
        )
        self.subcategory_income = self.make_subcategory(
            category=Category.objects.get(id=self.category_income.id)
        )
        self.subcategory_expense = self.make_subcategory(
            category=Category.objects.get(id=self.category_expense.id),
            sub_slug='slug_expense',
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
            subcategory=SubCategory.objects.get(id=self.subcategory_income.id),
            beneficiary=Beneficiary.objects.get(id=self.beneficiary.id),
            client=Client.objects.get(id=self.client_label.id),
            financial_cost_center=Financial.objects.get(id=self.cost_center.id),  # noqa: E501
            financial_account=Financial.objects.get(id=self.bank_account.id),
        )
        return super().setUp()

    # Testing going to home:index and session expires
    def test_board_index_session_expires_after_login(self):
        payload = {
            'whoami': 1,
            'login': 'jane.doe@email.com',
            'manager': False,
            'iss': datetime.now().strftime('%s'),
            'exp': (datetime.now() + timedelta(seconds=1)).strftime('%s')  # noqa: E501
        }
        session = self.client.session
        session.update({
            'auth': auth(payload)
        })
        session.save()
        self.sleep(2)
        response = self.client.get(reverse('board:index'), follow=True)
        self.assertEqual(
            'Your session has expired, please login.',
            response.context['error']
        )
        self.assertTemplateUsed(
            response, 'home/pages/index.html'
        )

    # Testing the returned function on each view function
    def test_board_index_view_function(self):
        view = resolve(reverse('board:index'))
        self.assertIs(
            view.func.__module__, index_view.BoardIndexView.__module__
        )

    def test_board_index_new_view_function(self):
        view = resolve(reverse('board:index_new'))
        self.assertIs(
            view.func.__module__, index_view.BoardIndexView.__module__
        )

    def test_board_index_edit_view_function(self):
        view = resolve(reverse('board:index_edit'))
        self.assertIs(
            view.func.__module__, index_view.BoardIndexView.__module__
        )

    def test_board_index_delete_view_function(self):
        view = resolve(reverse('board:index_delete'))
        self.assertIs(
            view.func.__module__, index_view.BoardIndexView.__module__
        )

    # Testing wich template is loaded on index view function

    # without credentials
    def test_board_index_no_credentials(self):
        response = self.client.get(
            reverse('board:index'),
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
    def test_board_index_with_credentials(self):
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
        response = self.client.get(reverse('board:index'))
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('error', response.context.keys())
        self.assertNotIn('success', response.context.keys())
        self.assertTemplateUsed(
            response, 'board/pages/index.html'
        )

    # Testing adding entry date with bad and empty data
    @parameterized.expand([
        (''),  # empty data
        (';;;;;'),  # invalid data
        ('2022-02-31'),  # invalid date
        ('202222-01-15'),  # invalid date
    ])
    def test_board_index_new_entry_date_errors(self, value):
        self.client.post(
            reverse('home:index_auth'),
            data={
                'use_login': 'jane.doe@email.com',
                'use_password': '$Trong1234'
            },
            follow=True
        )
        response = self.client.post(
            reverse('board:index_new'),
            data={
                'entry_date': value,
                'subcategory': hash_gen(self.subcategory_income.sub_slug),
                'description': 'Description',
                'beneficiary': hash_gen(self.beneficiary.ben_slug),
                'client': hash_gen(self.client_label.cli_slug),
                'cost_center': hash_gen(self.cost_center.fin_slug),
                'condition': 1,
                'account': hash_gen(self.bank_account.fin_slug),
                'amount': '1,002.03',
            },
            follow=True
        )
        self.assertRedirects(response, reverse('board:index'), 302)
        self.assertIn('error', response.context.keys())
        self.assertNotIn('success', response.context.keys())
        self.assertIn('entries', response.context.keys())
        self.assertIn('categories', response.context.keys())
        self.assertIn('beneficiaries', response.context.keys())
        self.assertIn('clients', response.context.keys())
        self.assertIn('cost_centers', response.context.keys())
        self.assertIn('accounts', response.context.keys())
        self.assertIn('analytic', response.context.keys())
        self.assertIn('filter', response.context.keys())
        self.assertIn('pages', response.context.keys())
        if not value:
            self.assertEqual(
                'Invalid data, new entry not registered:<br />This field is required.',  # noqa: E501
                response.context['error']
            )
        else:
            self.assertEqual(
                'Invalid data, new entry not registered:<br />Enter a valid date.',  # noqa: E501
                response.context['error']
            )
        self.assertTemplateUsed(response, 'board/pages/index.html')

    # Testing adding description with bad data
    def test_board_index_new_description_error(self):
        self.client.post(
            reverse('home:index_auth'),
            data={
                'use_login': 'jane.doe@email.com',
                'use_password': '$Trong1234'
            },
            follow=True
        )
        response = self.client.post(
            reverse('board:index_new'),
            data={
                'entry_date': '2022-01-05',
                'subcategory': hash_gen(self.subcategory_income.sub_slug),
                'description': 'Description;;;;;',
                'beneficiary': hash_gen(self.beneficiary.ben_slug),
                'client': hash_gen(self.client_label.cli_slug),
                'cost_center': hash_gen(self.cost_center.fin_slug),
                'condition': 1,
                'account': hash_gen(self.bank_account.fin_slug),
                'amount': '1,002.03',
            },
            follow=True
        )
        self.assertRedirects(response, reverse('board:index'), 302)
        self.assertIn('error', response.context.keys())
        self.assertNotIn('success', response.context.keys())
        self.assertIn('entries', response.context.keys())
        self.assertIn('categories', response.context.keys())
        self.assertIn('beneficiaries', response.context.keys())
        self.assertIn('clients', response.context.keys())
        self.assertIn('cost_centers', response.context.keys())
        self.assertIn('accounts', response.context.keys())
        self.assertIn('analytic', response.context.keys())
        self.assertIn('filter', response.context.keys())
        self.assertIn('pages', response.context.keys())
        self.assertEqual(
            'Invalid data, new entry not registered:<br />'
            'Entry cannot contain disallowed characters. e.g. &quot;;&quot;.',
            response.context['error']
        )
        self.assertTemplateUsed(response, 'board/pages/index.html')

    # Testing adding amount with bad and empty data
    @parameterized.expand([
        (''),  # empty data
        (';;;;;'),  # invalid data
        ('teste@'),  # only string
    ])
    def test_board_index_new_amount_errors(self, value):
        self.client.post(
            reverse('home:index_auth'),
            data={
                'use_login': 'jane.doe@email.com',
                'use_password': '$Trong1234'
            },
            follow=True
        )
        response = self.client.post(
            reverse('board:index_new'),
            data={
                'entry_date': '2022-01-05',
                'subcategory': hash_gen(self.subcategory_income.sub_slug),
                'description': 'Description',
                'beneficiary': hash_gen(self.beneficiary.ben_slug),
                'client': hash_gen(self.client_label.cli_slug),
                'cost_center': hash_gen(self.cost_center.fin_slug),
                'condition': 1,
                'account': hash_gen(self.bank_account.fin_slug),
                'amount': value,
            },
            follow=True
        )
        self.assertRedirects(response, reverse('board:index'), 302)
        self.assertIn('error', response.context.keys())
        self.assertNotIn('success', response.context.keys())
        self.assertIn('entries', response.context.keys())
        self.assertIn('categories', response.context.keys())
        self.assertIn('beneficiaries', response.context.keys())
        self.assertIn('clients', response.context.keys())
        self.assertIn('cost_centers', response.context.keys())
        self.assertIn('accounts', response.context.keys())
        self.assertIn('analytic', response.context.keys())
        self.assertIn('filter', response.context.keys())
        self.assertIn('pages', response.context.keys())
        if not value:
            self.assertEqual(
                'Invalid data, new entry not registered:<br />This field is required.',  # noqa: E501
                response.context['error']
            )
        else:
            self.assertEqual(
                'Invalid data, new entry not registered:<br />Enter a number.',
                response.context['error']
            )
        self.assertTemplateUsed(response, 'board/pages/index.html')

    # Testing adding new entry
    def test_board_index_new_entry(self):
        self.client.post(
            reverse('home:index_auth'),
            data={
                'use_login': 'jane.doe@email.com',
                'use_password': '$Trong1234'
            },
            follow=True
        )
        response = self.client.post(
            reverse('board:index_new'),
            data={
                'entry_date': '2022-01-05',
                'subcategory': hash_gen(self.subcategory_income.sub_slug),
                'description': 'Description',
                'beneficiary': hash_gen(self.beneficiary.ben_slug),
                'client': hash_gen(self.client_label.cli_slug),
                'cost_center': hash_gen(self.cost_center.fin_slug),
                'condition': 1,
                'account': hash_gen(self.bank_account.fin_slug),
                'amount': '1,002.03',
            },
            follow=True
        )
        self.assertRedirects(response, reverse('board:index'), 302)
        self.assertNotIn('error', response.context.keys())
        self.assertIn('success', response.context.keys())
        self.assertIn('entries', response.context.keys())
        self.assertIn('categories', response.context.keys())
        self.assertIn('beneficiaries', response.context.keys())
        self.assertIn('clients', response.context.keys())
        self.assertIn('cost_centers', response.context.keys())
        self.assertIn('accounts', response.context.keys())
        self.assertIn('analytic', response.context.keys())
        self.assertIn('filter', response.context.keys())
        self.assertIn('pages', response.context.keys())
        self.assertEqual(
            'New entry added successfully.', response.context['success']
        )
        self.assertEqual(
            str(response.context['entries'][0]['rel_overall_balance']),
            '2002.030'
        )
        response = self.client.get(
            reverse('board:index'),
            data={
                'm': '1',
                'y': '2022'
            }
        )
        self.assertEqual(
            str(response.context['entries'][0]['rel_overall_balance']),
            '1002.030'
        )
        self.assertTemplateUsed(response, 'board/pages/index.html')

    # Testing editing entry date with bad and empty data
    @parameterized.expand([
        (''),  # empty data
        (';;;;;'),  # invalid data
        ('2022-02-31'),  # invalid date
        ('202222-01-15'),  # invalid date
    ])
    def test_board_index_edit_entry_date_errors(self, value):
        self.client.post(
            reverse('home:index_auth'),
            data={
                'use_login': 'jane.doe@email.com',
                'use_password': '$Trong1234'
            },
            follow=True
        )
        response = self.client.post(
            reverse('board:index_edit'),
            data={
                'entry_date_edit': value,
                'subcategory_edit': hash_gen(self.subcategory_income.sub_slug),
                'description_edit': 'Description',
                'beneficiary_edit': hash_gen(self.beneficiary.ben_slug),
                'client_edit': hash_gen(self.client_label.cli_slug),
                'cost_center_edit': hash_gen(self.cost_center.fin_slug),
                'condition_edit': 1,
                'account_edit': hash_gen(self.bank_account.fin_slug),
                'amount_edit': '1,002.03',
                'edit_index': hash_gen(self.entry.rel_slug)
            },
            follow=True
        )
        self.assertRedirects(response, reverse('board:index'), 302)
        self.assertIn('error', response.context.keys())
        self.assertNotIn('success', response.context.keys())
        self.assertIn('entries', response.context.keys())
        self.assertIn('categories', response.context.keys())
        self.assertIn('beneficiaries', response.context.keys())
        self.assertIn('clients', response.context.keys())
        self.assertIn('cost_centers', response.context.keys())
        self.assertIn('accounts', response.context.keys())
        self.assertIn('analytic', response.context.keys())
        self.assertIn('filter', response.context.keys())
        self.assertIn('pages', response.context.keys())
        if not value:
            self.assertEqual(
                'Invalid data, entry not edited:<br />This field is required.',
                response.context['error']
            )
        else:
            self.assertEqual(
                'Invalid data, entry not edited:<br />Enter a valid date.',
                response.context['error']
            )
        self.assertTemplateUsed(response, 'board/pages/index.html')

    # Testing editing description with bad data
    def test_board_index_edit_description_error(self):
        self.client.post(
            reverse('home:index_auth'),
            data={
                'use_login': 'jane.doe@email.com',
                'use_password': '$Trong1234'
            },
            follow=True
        )
        response = self.client.post(
            reverse('board:index_edit'),
            data={
                'entry_date_edit': '2022-01-05',
                'subcategory_edit': hash_gen(self.subcategory_income.sub_slug),
                'description_edit': 'Description;;;;;',
                'beneficiary_edit': hash_gen(self.beneficiary.ben_slug),
                'client_edit': hash_gen(self.client_label.cli_slug),
                'cost_center_edit': hash_gen(self.cost_center.fin_slug),
                'condition_edit': 1,
                'account_edit': hash_gen(self.bank_account.fin_slug),
                'amount_edit': '1,002.03',
                'edit_index': hash_gen(self.entry.rel_slug)
            },
            follow=True
        )
        self.assertRedirects(response, reverse('board:index'), 302)
        self.assertIn('error', response.context.keys())
        self.assertNotIn('success', response.context.keys())
        self.assertIn('entries', response.context.keys())
        self.assertIn('categories', response.context.keys())
        self.assertIn('beneficiaries', response.context.keys())
        self.assertIn('clients', response.context.keys())
        self.assertIn('cost_centers', response.context.keys())
        self.assertIn('accounts', response.context.keys())
        self.assertIn('analytic', response.context.keys())
        self.assertIn('filter', response.context.keys())
        self.assertIn('pages', response.context.keys())
        self.assertEqual(
            'Invalid data, entry not edited:<br />'
            'Entry cannot contain disallowed characters. e.g. &quot;;&quot;.',
            response.context['error']
        )
        self.assertTemplateUsed(response, 'board/pages/index.html')

    # Testing editing amount with bad and empty data
    @parameterized.expand([
        (''),  # empty data
        (';;;;;'),  # invalid data
        ('teste@'),  # only string
    ])
    def test_board_index_edit_amount_errors(self, value):
        self.client.post(
            reverse('home:index_auth'),
            data={
                'use_login': 'jane.doe@email.com',
                'use_password': '$Trong1234'
            },
            follow=True
        )
        response = self.client.post(
            reverse('board:index_edit'),
            data={
                'entry_date_edit': '2022-01-05',
                'subcategory_edit': hash_gen(self.subcategory_income.sub_slug),
                'description_edit': 'Description',
                'beneficiary_edit': hash_gen(self.beneficiary.ben_slug),
                'client_edit': hash_gen(self.client_label.cli_slug),
                'cost_center_edit': hash_gen(self.cost_center.fin_slug),
                'condition_edit': 1,
                'account_edit': hash_gen(self.bank_account.fin_slug),
                'amount_edit': value,
                'edit_index': hash_gen(self.entry.rel_slug)
            },
            follow=True
        )
        self.assertRedirects(response, reverse('board:index'), 302)
        self.assertIn('error', response.context.keys())
        self.assertNotIn('success', response.context.keys())
        self.assertIn('entries', response.context.keys())
        self.assertIn('categories', response.context.keys())
        self.assertIn('beneficiaries', response.context.keys())
        self.assertIn('clients', response.context.keys())
        self.assertIn('cost_centers', response.context.keys())
        self.assertIn('accounts', response.context.keys())
        self.assertIn('analytic', response.context.keys())
        self.assertIn('filter', response.context.keys())
        self.assertIn('pages', response.context.keys())
        if not value:
            self.assertEqual(
                'Invalid data, entry not edited:<br />This field is required.',
                response.context['error']
            )
        else:
            self.assertEqual(
                'Invalid data, entry not edited:<br />Enter a number.',
                response.context['error']
            )
        self.assertTemplateUsed(response, 'board/pages/index.html')

    # Testing editing new entry
    def test_board_index_edit_entry(self):
        self.client.post(
            reverse('home:index_auth'),
            data={
                'use_login': 'jane.doe@email.com',
                'use_password': '$Trong1234'
            },
            follow=True
        )
        response = self.client.post(
            reverse('board:index_edit'),
            data={
                'entry_date_edit': '2022-01-05',
                'subcategory_edit': hash_gen(self.subcategory_income.sub_slug),
                'description_edit': 'Description',
                'beneficiary_edit': hash_gen(self.beneficiary.ben_slug),
                'client_edit': hash_gen(self.client_label.cli_slug),
                'cost_center_edit': hash_gen(self.cost_center.fin_slug),
                'condition_edit': 1,
                'account_edit': hash_gen(self.bank_account.fin_slug),
                'amount_edit': '1,002.03',
                'edit_index': hash_gen(self.entry.rel_slug)
            },
            follow=True
        )
        self.assertRedirects(response, reverse('board:index'), 302)
        self.assertNotIn('error', response.context.keys())
        self.assertIn('success', response.context.keys())
        self.assertIn('entries', response.context.keys())
        self.assertIn('categories', response.context.keys())
        self.assertIn('beneficiaries', response.context.keys())
        self.assertIn('clients', response.context.keys())
        self.assertIn('cost_centers', response.context.keys())
        self.assertIn('accounts', response.context.keys())
        self.assertIn('analytic', response.context.keys())
        self.assertIn('filter', response.context.keys())
        self.assertIn('pages', response.context.keys())
        self.assertEqual(
            'Entry edited successfully.', response.context['success']
        )
        self.assertFalse(response.context['entries'])
        self.assertTrue(response.context['past'])
        response = self.client.get(
            reverse('board:index'),
            data={
                'm': '1',
                'y': '2022'
            }
        )
        self.assertEqual(
            str(response.context['entries'][0]['rel_overall_balance']),
            '1002.030'
        )
        self.assertFalse(response.context['past'])
        self.assertTemplateUsed(response, 'board/pages/index.html')

    # Testing deleting entry
    def test_board_index_delete_entry(self):
        self.client.post(
            reverse('home:index_auth'),
            data={
                'use_login': 'jane.doe@email.com',
                'use_password': '$Trong1234'
            },
            follow=True
        )
        response = self.client.post(
            reverse('board:index_delete'),
            data={
                'del_index': hash_gen(str(self.entry.rel_slug)),
            },
            follow=True
        )
        self.assertRedirects(response, reverse('board:index'), 302)
        self.assertNotIn('error', response.context.keys())
        self.assertIn('success', response.context.keys())
        self.assertIn('entries', response.context.keys())
        self.assertIn('categories', response.context.keys())
        self.assertIn('beneficiaries', response.context.keys())
        self.assertIn('clients', response.context.keys())
        self.assertIn('cost_centers', response.context.keys())
        self.assertIn('accounts', response.context.keys())
        self.assertIn('analytic', response.context.keys())
        self.assertIn('filter', response.context.keys())
        self.assertIn('pages', response.context.keys())
        self.assertEqual(
            'Entry removed successfully.', response.context['success']
        )
        self.assertTemplateUsed(
            response, 'board/pages/index.html'
        )
        response = self.client.get(
            reverse('board:index'),
            data={
                'm': '5',
                'y': '2022'
            }
        )
        self.assertFalse(response.context['entries'])

    # testing pagination
    def test_board_index_pagination(self):
        self.client.post(
            reverse('home:index_auth'),
            data={
                'use_login': 'jane.doe@email.com',
                'use_password': '$Trong1234'
            },
            follow=True
        )

        for i in range(1, 30):
            subcategory_id = self.subcategory_income.id if i % 2 == 0 else self.subcategory_expense.id  # noqa: E501
            self.make_release(
                user=User.objects.get(id=self.user.id),
                rel_slug=i,
                rel_entry_date=f'2022-05-{i}',
                subcategory=SubCategory.objects.get(id=subcategory_id),
                beneficiary=Beneficiary.objects.get(id=self.beneficiary.id),
                client=Client.objects.get(id=self.client_label.id),
                financial_cost_center=Financial.objects.get(id=self.cost_center.id),  # noqa: E501
                financial_account=Financial.objects.get(id=self.bank_account.id),  # noqa: E501
                rel_sqn=i+1
            )

        with patch('board.views.index_view.PG_LIMIT', new=5):
            response = self.client.get(reverse('board:index'))
            self.assertEqual(
                response.context['pages']['pg_range'], [1, 2, 3, 4, 5]
            )

            response = self.client.get(
                reverse('board:index'),
                data={
                    'm': '5',
                    'y': '2022',
                    'pg': 5
                }
            )
            self.assertEqual(
                response.context['pages']['pg_range'], [2, 3, 4, 5, 6]
            )
            self.assertEqual(response.context['pages']['total_pg'], 6)

            response = self.client.get(
                reverse('board:index'),
                data={
                    'm': '5',
                    'y': '2022',
                    'pg': 6
                }
            )
            self.assertEqual(
                response.context['pages']['pg_range'], [2, 3, 4, 5, 6]
            )
            self.assertEqual(response.context['pages']['total_pg'], 6)

            response = self.client.get(
                reverse('board:index'),
                data={
                    'm': '5',
                    'y': '2022',
                    'pg': 4
                }
            )
            self.assertEqual(
                response.context['pages']['pg_range'], [2, 3, 4, 5, 6]
            )
            self.assertEqual(response.context['pages']['total_pg'], 6)
