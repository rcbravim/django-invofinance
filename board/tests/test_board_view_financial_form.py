import pytest
from board.tests.test_board_helper import BoardHelperMixin
from board.views import labels_financial_form_view
from django.test import TestCase
from django.urls import resolve, reverse
from home.models import User
from home.tests.test_home_helper import HomeHelperMixin
from library.utils.auth import auth
from library.utils.helper import hash_gen
from parameterized import parameterized


@pytest.mark.fast
class TestBoardViewFinancialForm(TestCase, HomeHelperMixin, BoardHelperMixin):
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
    def test_board_labels_financial_form_view_function(self):
        view = resolve(reverse('board:labels_financial_form'))
        self.assertIs(
            view.func.__module__,
            labels_financial_form_view.LabelsFinancialFormView.__module__
        )

    # Testing wich template is loaded on
    # labels_financial_form view function

    # without credentials
    def test_board_labels_financial_form_no_credentials(self):
        response = self.client.get(
            reverse('board:labels_financial_form'),
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
    def test_board_labels_financial_form_with_credentials(self):
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
        response = self.client.get(reverse('board:labels_financial_form'))
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('error', response.context.keys())
        self.assertNotIn('success', response.context.keys())
        self.assertTemplateUsed(
            response, 'board/pages/labels_financial_form.html'
        )

    # Testing adding cost_center with bad data and repeated
    @parameterized.expand([
        ('CostCenter'),  # duplicated data
        (';;;;;'),  # invalid data
    ])
    def test_board_labels_financial_form_new_cost_center_errors(self, value):
        self.client.post(
            reverse('home:index_auth'),
            data={
                'use_login': 'jane.doe@email.com',
                'use_password': '$Trong1234'
            },
            follow=True
        )
        response = self.client.post(
            reverse('board:labels_financial_form_new'),
            data={
                'cost_center': value,
                'label_type': 'CC'
            },
            follow=True
        )
        self.assertRedirects(
            response, reverse('board:labels_financial_form'), 302
        )
        self.assertIn('error', response.context.keys())
        self.assertNotIn('success', response.context.keys())
        if value == 'CostCenter':
            self.assertEqual(
                'Invalid data, cost center not registered:<br />This '
                'cost center is already register in our database and cannot be used.',  # noqa: E501
                response.context['error']
            )
        else:
            self.assertEqual(
                'Invalid data, cost center not registered:<br />'
                'Entry cannot contain disallowed characters. e.g. &quot;;&quot;.',  # noqa: E501
                response.context['error']
            )
        self.assertTemplateUsed(
            response, 'board/pages/labels_financial_form.html'
        )

    # Testing adding new cost center
    def test_board_labels_financial_form_new_adding_new_cost_center(self):
        self.client.post(
            reverse('home:index_auth'),
            data={
                'use_login': 'jane.doe@email.com',
                'use_password': '$Trong1234'
            },
            follow=True
        )
        response = self.client.post(
            reverse('board:labels_financial_form_new'),
            data={
                'cost_center': 'ValidCostCenter',
                'label_type': 'CC'
            },
            follow=True
        )
        self.assertRedirects(
            response, reverse('board:labels_financial_form'), 302
        )
        self.assertIn('success', response.context.keys())
        self.assertEqual(
            'Cost center added successfully.', response.context['success']
        )
        self.assertTemplateUsed(
            response, 'board/pages/labels_financial_form.html'
        )

    # Testing adding description with bad data
    def test_board_labels_financial_form_new_description_bad_data(self):
        self.client.post(
            reverse('home:index_auth'),
            data={
                'use_login': 'jane.doe@email.com',
                'use_password': '$Trong1234'
            },
            follow=True
        )
        response = self.client.post(
            reverse('board:labels_financial_form_new'),
            data={
                'cost_center': 'ValidCostCenter',
                'description': 'Description;;;',
                'label_type': 'CC'
            },
            follow=True
        )
        self.assertRedirects(
            response, reverse('board:labels_financial_form'), 302
        )
        self.assertIn('error', response.context.keys())
        self.assertNotIn('success', response.context.keys())
        self.assertTemplateUsed(
            response, 'board/pages/labels_financial_form.html'
        )
        self.assertEqual(
            'Invalid data, cost center not registered:<br />'
            'Entry cannot contain disallowed characters. e.g. &quot;;&quot;.',
            response.context['error']
        )

    # Testing adding description with good data
    def test_board_labels_financial_form_new_adding_new_cost_center_complete(self):   # noqa: E501
        self.client.post(
            reverse('home:index_auth'),
            data={
                'use_login': 'jane.doe@email.com',
                'use_password': '$Trong1234'
            },
            follow=True
        )
        response = self.client.post(
            reverse('board:labels_financial_form_new'),
            data={
                'cost_center': 'ValidCostCenter',
                'description': 'Description',
                'label_type': 'CC'
            },
            follow=True
        )
        self.assertRedirects(
            response, reverse('board:labels_financial_form'), 302
        )
        self.assertIn('success', response.context.keys())
        self.assertEqual(
            'Cost center added successfully.', response.context['success']
        )
        self.assertTemplateUsed(
            response, 'board/pages/labels_financial_form.html'
        )

    # Testing adding bank with bad data
    def test_board_labels_financial_form_new_bank_name_bad_data(self):
        self.client.post(
            reverse('home:index_auth'),
            data={
                'use_login': 'jane.doe@email.com',
                'use_password': '$Trong1234'
            },
            follow=True
        )
        response = self.client.post(
            reverse('board:labels_financial_form_new'),
            data={
                'bank': ';;;;;',
                'branch': '1234',
                'account': '123456789',
                'label_type': 'BA'
            },
            follow=True
        )
        self.assertRedirects(
            response, reverse('board:labels_financial_form'), 302
        )
        self.assertIn('error', response.context.keys())
        self.assertNotIn('success', response.context.keys())
        self.assertTemplateUsed(
            response, 'board/pages/labels_financial_form.html'
        )
        self.assertEqual(
            'Invalid data, bank account not registered:<br />'
            'Entry cannot contain disallowed characters. e.g. &quot;;&quot;.',
            response.context['error']
        )

    # Testing adding branch with bad data
    @parameterized.expand([
        (';;;;;'),  # invalid data
        ('teste@'),  # only string
    ])
    def test_board_labels_financial_form_new_branch_erro(self, value):
        self.client.post(
            reverse('home:index_auth'),
            data={
                'use_login': 'jane.doe@email.com',
                'use_password': '$Trong1234'
            },
            follow=True
        )
        response = self.client.post(
            reverse('board:labels_financial_form_new'),
            data={
                'bank': 'ValidBank',
                'branch': value,
                'account': '123456789',
                'label_type': 'BA'
            },
            follow=True
        )
        self.assertRedirects(
            response, reverse('board:labels_financial_form'), 302
        )
        self.assertIn('error', response.context.keys())
        self.assertNotIn('success', response.context.keys())
        self.assertTemplateUsed(
            response, 'board/pages/labels_financial_form.html'
        )
        if ';' in value:
            self.assertEqual(
                'Invalid data, bank account not registered:<br />'
                'Entry cannot contain disallowed characters. e.g. &quot;;&quot;.',  # noqa: E501
                response.context['error']
            )
        else:
            self.assertEqual(
                'Invalid data, bank account not registered:<br />'
                'Branch should must consist of numbers only.',
                response.context['error']
            )

    # Testing adding account with bad data and duplicated
    @parameterized.expand([
        ('123456789'),
        (';;;;;'),  # invalid data
        ('teste@'),  # only string
    ])
    def test_board_labels_financial_form_new_account_erro(self, value):
        self.client.post(
            reverse('home:index_auth'),
            data={
                'use_login': 'jane.doe@email.com',
                'use_password': '$Trong1234'
            },
            follow=True
        )
        response = self.client.post(
            reverse('board:labels_financial_form_new'),
            data={
                'bank': 'BankName',
                'branch': '1234',
                'account': value,
                'label_type': 'BA'
            },
            follow=True
        )
        self.assertRedirects(
            response, reverse('board:labels_financial_form'), 302
        )
        self.assertIn('error', response.context.keys())
        self.assertNotIn('success', response.context.keys())
        self.assertTemplateUsed(
            response, 'board/pages/labels_financial_form.html'
        )
        if value == '123456789':
            self.assertEqual(
                'Invalid data, bank account not registered:<br />'
                'This bank account is already register in our database and cannot be used.',  # noqa: E501
                response.context['error']
            )
        elif ';' in value:
            self.assertEqual(
                'Invalid data, bank account not registered:<br />'
                'Entry cannot contain disallowed characters. e.g. &quot;;&quot;.',  # noqa: E501
                response.context['error']
            )
        else:
            self.assertEqual(
                'Invalid data, bank account not registered:<br />'
                'Account should must consist of numbers only.',
                response.context['error']
            )

    # Testing adding bank with good data
    def test_board_labels_financial_form_new_bank(self):
        self.client.post(
            reverse('home:index_auth'),
            data={
                'use_login': 'jane.doe@email.com',
                'use_password': '$Trong1234'
            },
            follow=True
        )
        response = self.client.post(
            reverse('board:labels_financial_form_new'),
            data={
                'bank': 'ValidBank',
                'branch': '1234',
                'account': '123456789',
                'label_type': 'BA'
            },
            follow=True
        )
        self.assertRedirects(
            response, reverse('board:labels_financial_form'), 302
        )
        self.assertNotIn('error', response.context.keys())
        self.assertIn('success', response.context.keys())
        self.assertTemplateUsed(
            response, 'board/pages/labels_financial_form.html'
        )
        self.assertEqual(
            'Bank account added successfully.',
            response.context['success']
        )
