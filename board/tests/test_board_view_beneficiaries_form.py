import pytest
from board.models import BeneficiaryCategory
from board.tests.test_board_helper import BoardHelperMixin
from board.views import labels_beneficiaries_form_view
from django.test import TestCase
from django.urls import resolve, reverse
from home.models import User
from home.tests.test_home_helper import HomeHelperMixin
from library.utils.auth import auth
from library.utils.helper import hash_gen
from parameterized import parameterized


@pytest.mark.fast
class TestBoardViewBeneficiariesForm(TestCase, HomeHelperMixin,
                                     BoardHelperMixin):
    def setUp(self) -> None:
        self.user = self.make_user(use_is_valid=True)
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

    # Testing the returned function on each view function
    def test_board_labels_beneficiaries_form_view_function(self):
        view = resolve(reverse('board:labels_beneficiaries_form'))
        self.assertIs(
            view.func.__module__,
            labels_beneficiaries_form_view.LabelsBeneficiariesFormView.__module__  # noqa: E501
        )

    def test_board_labels_beneficiaries_form_new_view_function(self):
        view = resolve(reverse('board:labels_beneficiaries_form_new'))
        self.assertIs(
            view.func.__module__,
            labels_beneficiaries_form_view.LabelsBeneficiariesFormView.__module__  # noqa: E501
        )

    def test_board_labels_beneficiaries_form_delete_type_view_function(self):
        view = resolve(reverse('board:labels_beneficiaries_form_delete_type'))
        self.assertIs(
            view.func.__module__,
            labels_beneficiaries_form_view.LabelsBeneficiariesFormView.__module__  # noqa: E501
        )

    # Testing wich template is loaded on
    # labels_beneficiaries_form view function

    # without credentials
    def test_board_labels_beneficiaries_form_no_credentials(self):
        response = self.client.get(
            reverse('board:labels_beneficiaries_form'),
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
    def test_board_labels_beneficiaries_form_with_credentials(self):
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
        response = self.client.get(reverse('board:labels_beneficiaries_form'))
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('error', response.context.keys())
        self.assertNotIn('success', response.context.keys())
        self.assertIn('types', response.context.keys())
        self.assertTemplateUsed(
            response, 'board/pages/labels_beneficiaries_form.html'
        )

    # Testing deleting beneficiary type
    def test_board_labels_beneficiaries_form_delete_type_deleting_type(self):
        self.client.post(
            reverse('home:index_auth'),
            data={
                'use_login': 'jane.doe@email.com',
                'use_password': '$Trong1234'
            },
            follow=True
        )
        response = self.client.post(
            reverse('board:labels_beneficiaries_form_delete_type'),
            data={'description': hash_gen(self.category.cat_slug)},
            follow=True
        )
        self.assertRedirects(
            response, reverse('board:labels_beneficiaries_form'), 302
        )
        self.assertIn('success', response.context.keys())
        self.assertNotIn('error', response.context.keys())
        self.assertEqual(
            'Beneficiary type removed successfully.',
            response.context['success']
        )
        self.assertIn('types', response.context.keys())
        self.assertNotIn('Description', str(response.context['types']))
        self.assertFalse(response.context['types'])
        self.assertTemplateUsed(
            response, 'board/pages/labels_beneficiaries_form.html'
        )

    # Testing adding beneficiary type with bad data, empty and repeated
    @parameterized.expand([
        ('Description'),  # duplicated data
        (''),  # empty data
        (';;;;;'),  # invalid data
    ])
    def test_board_labels_beneficiaries_form_new_type_errors(self, value):
        self.client.post(
            reverse('home:index_auth'),
            data={
                'use_login': 'jane.doe@email.com',
                'use_password': '$Trong1234'
            },
            follow=True
        )
        response = self.client.post(
            reverse('board:labels_beneficiaries_form_new'),
            data={
                'description': value,
                'name': 'NewName'
            },
            follow=True
        )
        self.assertRedirects(
            response, reverse('board:labels_beneficiaries_form'), 302
        )
        self.assertIn('error', response.context.keys())
        self.assertNotIn('success', response.context.keys())
        self.assertIn('types', response.context.keys())
        if value == 'Description':
            self.assertEqual(
                value, response.context['types'][0].get('cat_description')
            )
            self.assertEqual(
                'Invalid data, beneficiary type not registered:<br />This '
                'beneficiary type is already register in our database and cannot be used.',  # noqa: E501
                response.context['error']
            )
        else:
            self.assertNotEqual(
                value, response.context['types'][0].get('cat_description')
            )
            if not value:
                self.assertEqual(
                    'Invalid data, beneficiary type not registered:<br />This field is required.',  # noqa: E501
                    response.context['error']
                )
            else:
                self.assertEqual(
                    'Invalid data, beneficiary type not registered:<br />'
                    'Entry cannot contain disallowed characters. e.g. &quot;;&quot;.',  # noqa: E501
                    response.context['error']
                )
        self.assertTemplateUsed(
            response, 'board/pages/labels_beneficiaries_form.html'
        )

    # Testing adding new beneficiary
    def test_board_labels_beneficiaries_form_new_adding_new_beneficiary(self):
        self.client.post(
            reverse('home:index_auth'),
            data={
                'use_login': 'jane.doe@email.com',
                'use_password': '$Trong1234'
            },
            follow=True
        )
        response = self.client.post(
            reverse('board:labels_beneficiaries_form_new'),
            data={
                'description': hash_gen(self.category.cat_slug),
                'name': 'BeneficiaryNew'
            },
            follow=True
        )
        self.assertRedirects(
            response, reverse('board:labels_beneficiaries_form'), 302
        )
        self.assertIn('success', response.context.keys())
        self.assertEqual(
            'Beneficiary name added successfully.', response.context['success']
        )
        self.assertTemplateUsed(
            response, 'board/pages/labels_beneficiaries_form.html'
        )

    # Testing adding new type and beneficiary
    def test_board_labels_beneficiaries_form_new_adding_new_type_and_beneficiary(self):  # noqa: E501
        self.client.post(
            reverse('home:index_auth'),
            data={
                'use_login': 'jane.doe@email.com',
                'use_password': '$Trong1234'
            },
            follow=True
        )
        response = self.client.post(
            reverse('board:labels_beneficiaries_form_new'),
            data={
                'description': 'NewType',
                'name': 'BeneficiaryNew'
            },
            follow=True
        )
        self.assertRedirects(
            response, reverse('board:labels_beneficiaries_form'), 302
        )
        self.assertIn('success', response.context.keys())
        self.assertEqual(
            'Beneficiary type and name added successfully.',
            response.context['success']
        )
        self.assertTemplateUsed(
            response, 'board/pages/labels_beneficiaries_form.html'
        )

    # Testing adding beneficiary with bad data, empty and repeated
    @parameterized.expand([
        ('Beneficiary'),  # duplicated data
        (''),  # empty data
        (';;;;;'),  # invalid data
    ])
    def test_board_labels_beneficiaries_form_new_errors(self, value):
        self.client.post(
            reverse('home:index_auth'),
            data={
                'use_login': 'jane.doe@email.com',
                'use_password': '$Trong1234'
            },
            follow=True
        )
        response = self.client.post(
            reverse('board:labels_beneficiaries_form_new'),
            data={
                'description': hash_gen(self.category.cat_slug),
                'name': value
            },
            follow=True
        )
        self.assertRedirects(
            response, reverse('board:labels_beneficiaries_form'), 302
        )
        self.assertIn('error', response.context.keys())
        self.assertNotIn('success', response.context.keys())
        self.assertIn('types', response.context.keys())
        self.assertTemplateUsed(
            response, 'board/pages/labels_beneficiaries_form.html'
        )

        if value == 'Beneficiary':
            self.assertEqual(
                'Invalid data, beneficiary name not registered:<br />This '
                'beneficiary is already register in our database and cannot be used.',  # noqa: E501
                response.context['error']
            )
        elif not value:
            if not value:
                self.assertEqual(
                    'Invalid data, beneficiary name not registered:<br />This field is required.',  # noqa: E501
                    response.context['error']
                )
        else:
            self.assertEqual(
                'Invalid data, beneficiary name not registered:<br />'
                'Entry cannot contain disallowed characters. e.g. &quot;;&quot;.',  # noqa: E501
                response.context['error']
            )
