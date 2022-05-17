from unittest.mock import patch

import pytest
from board.models import BeneficiaryCategory
from board.tests.test_board_helper import BoardHelperMixin
from board.views import labels_beneficiaries_view
from django.test import TestCase
from django.urls import resolve, reverse
from home.models import User
from home.tests.test_home_helper import HomeHelperMixin
from library.utils.auth import auth
from library.utils.helper import hash_gen
from parameterized import parameterized


@pytest.mark.fast
class TestBoardViewBeneficiaries(TestCase, HomeHelperMixin, BoardHelperMixin):
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
    def test_board_labels_beneficiaries_view_function(self):
        view = resolve(reverse('board:labels_beneficiaries'))
        self.assertIs(
            view.func.__module__,
            labels_beneficiaries_view.LabelsBeneficiariesView.__module__
        )

    def test_board_labels_beneficiaries_edit_view_function(self):
        view = resolve(reverse('board:labels_beneficiaries_edit'))
        self.assertIs(
            view.func.__module__,
            labels_beneficiaries_view.LabelsBeneficiariesView.__module__
        )

    def test_board_labels_beneficiaries_delete_view_function(self):
        view = resolve(reverse('board:labels_beneficiaries_delete'))
        self.assertIs(
            view.func.__module__,
            labels_beneficiaries_view.LabelsBeneficiariesView.__module__
        )

    # Testing wich template is loaded on
    # labels_beneficiaries view function

    # without credentials
    def test_board_labels_beneficiaries_no_credentials(self):
        response = self.client.get(
            reverse('board:labels_beneficiaries'),
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
    def test_board_labels_beneficiaries_with_credentials(self):
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
        response = self.client.get(reverse('board:labels_beneficiaries'))
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('error', response.context.keys())
        self.assertNotIn('success', response.context.keys())
        self.assertIn('types', response.context.keys())
        self.assertIn('beneficiaries', response.context.keys())
        self.assertIn('filter', response.context.keys())
        self.assertIn('pages', response.context.keys())
        self.assertTemplateUsed(
            response, 'board/pages/labels_beneficiaries.html'
        )

    # testing pagination
    def test_board_labels_beneficiaries_pagination(self):
        self.client.post(
            reverse('home:index_auth'),
            data={
                'use_login': 'jane.doe@email.com',
                'use_password': '$Trong1234'
            },
            follow=True
        )

        for i in range(1, 100):
            self.make_beneficiary(
                ben_name='Beneficiary' + str(i),
                user=User.objects.get(id=self.user.id),
                beneficiary_category=BeneficiaryCategory.objects.get(
                    id=self.category.id
                ),
                ben_slug=i
            )

        with patch('board.views.labels_beneficiaries_view.PG_LIMIT', new=10):
            response = self.client.get(reverse('board:labels_beneficiaries'))
            self.assertEqual(
                response.context['pages']['pg_range'], [1, 2, 3, 4, 5]
            )

            response = self.client.get(
                reverse('board:labels_beneficiaries'),
                data={
                    'pg': 7
                }
            )
            self.assertEqual(
                response.context['pages']['pg_range'], [5, 6, 7, 8, 9]
            )
            self.assertEqual(response.context['pages']['total_pg'], 10)

            response = self.client.get(
                reverse('board:labels_beneficiaries'),
                data={
                    'pg': 10
                }
            )
            self.assertEqual(
                response.context['pages']['pg_range'], [6, 7, 8, 9, 10]
            )
            self.assertEqual(response.context['pages']['total_pg'], 10)

            response = self.client.get(
                reverse('board:labels_beneficiaries'),
                data={
                    'pg': 9
                }
            )
            self.assertEqual(
                response.context['pages']['pg_range'], [6, 7, 8, 9, 10]
            )
            self.assertEqual(response.context['pages']['total_pg'], 10)

    # testing filters
    def test_board_labels_beneficiaries_filters(self):
        self.client.post(
            reverse('home:index_auth'),
            data={
                'use_login': 'jane.doe@email.com',
                'use_password': '$Trong1234'
            },
            follow=True
        )

        new_category = self.make_beneficiary_category(
            cat_slug=10
        )

        self.make_beneficiary(
            ben_name='Beneficiary-other',
            user=User.objects.get(id=self.user.id),
            beneficiary_category=BeneficiaryCategory.objects.get(
                id=new_category.id
            ),
            ben_slug='other'
        )

        for i in range(1, 100):
            self.make_beneficiary(
                ben_name='Beneficiary' + str(i),
                user=User.objects.get(id=self.user.id),
                beneficiary_category=BeneficiaryCategory.objects.get(
                    id=self.category.id
                ),
                ben_slug=i
            )

        with patch('board.views.labels_beneficiaries_view.PG_LIMIT', new=10):
            response = self.client.get(
                reverse('board:labels_beneficiaries'),
                data={
                    'type': hash_gen('10')
                }
            )

            self.assertEqual(response.context['pages']['pg_range'], [1])
            self.assertEqual(response.context['pages']['total_pg'], 1)
            self.assertEqual(len(response.context['beneficiaries']), 1)
            self.assertEqual(
                response.context['filter']['type'], hash_gen(str(10))
            )
            self.assertEqual(
                response.context['beneficiaries'][0]['ben_name'],
                'Beneficiary-other'
            )

            response = self.client.get(
                reverse('board:labels_beneficiaries'),
                data={
                    'search': '33'
                }
            )
            self.assertEqual(response.context['pages']['pg_range'], [1])
            self.assertEqual(response.context['pages']['total_pg'], 1)
            self.assertEqual(len(response.context['beneficiaries']), 1)
            self.assertEqual(response.context['filter']['search'], '33')
            self.assertEqual(
                response.context['beneficiaries'][0]['ben_name'],
                'Beneficiary33'
            )

            response = self.client.get(
                reverse('board:labels_beneficiaries'),
                data={
                    'search': 'Beneficiary',
                    'pg': 6
                }
            )
            self.assertEqual(
                response.context['pages']['pg_range'], [4, 5, 6, 7, 8]
            )
            self.assertEqual(response.context['pages']['total_pg'], 11)
            self.assertEqual(len(response.context['beneficiaries']), 10)
            self.assertEqual(
                response.context['filter']['search'], 'Beneficiary'
            )

            response = self.client.get(
                reverse('board:labels_beneficiaries'),
                data={
                    'search': 'Beneficiary',
                    'pg': 1
                }
            )
            self.assertEqual(
                response.context['pages']['pg_range'], [1, 2, 3, 4, 5]
            )
            self.assertEqual(response.context['pages']['total_pg'], 11)
            self.assertEqual(len(response.context['beneficiaries']), 10)
            self.assertEqual(
                response.context['filter']['search'], 'Beneficiary'
            )
            self.assertEqual(
                response.context['beneficiaries'][1]['ben_name'],
                'Beneficiary-other'
            )

            response = self.client.get(
                reverse('board:labels_beneficiaries'),
                data={
                    'search': 'nada'
                }
            )
            self.assertEqual(response.context['pages']['pg_range'], [])
            self.assertEqual(response.context['pages']['total_pg'], 0)
            self.assertEqual(len(response.context['beneficiaries']), 0)
            self.assertEqual(
                response.context['filter']['search'], 'nada'
            )

    # Testing editing beneficiary type with bad data, empty and repeated
    @parameterized.expand([
        ('Description-other'),  # duplicated data
        (''),  # empty data
        (';;;;;'),  # invalid data
    ])
    def test_board_labels_beneficiaries_edit_type_errors(self, value):
        self.client.post(
            reverse('home:index_auth'),
            data={
                'use_login': 'jane.doe@email.com',
                'use_password': '$Trong1234'
            },
            follow=True
        )

        self.make_beneficiary_category(
            user=User.objects.get(id=self.user.id),
            cat_description='Description-other',
            cat_slug='other'
        )

        response = self.client.post(
            reverse('board:labels_beneficiaries_edit'),
            data={
                'description': value,
                'edit_beneficiary': hash_gen(str(self.beneficiary.ben_slug)),
                'name': self.beneficiary.ben_name
            },
            follow=True
        )
        self.assertRedirects(
            response, reverse('board:labels_beneficiaries'), 302
        )
        self.assertIn('error', response.context.keys())
        self.assertNotIn('success', response.context.keys())
        self.assertIn('types', response.context.keys())
        self.assertIn('beneficiaries', response.context.keys())
        self.assertIn('filter', response.context.keys())
        self.assertIn('pages', response.context.keys())
        if value == 'Description-other':
            self.assertEqual(
                'Invalid data, beneficiary type not edited:<br />This '
                'beneficiary type is already register in our database and cannot be used.',  # noqa: E501
                response.context['error']
            )
        elif not value:
            self.assertEqual(
                'Invalid data, beneficiary type not edited:<br />This field is required.',  # noqa: E501
                response.context['error']
            )
        else:
            self.assertEqual(
                'Invalid data, beneficiary type not edited:<br />'
                'Entry cannot contain disallowed characters. e.g. &quot;;&quot;.',  # noqa: E501
                response.context['error']
            )
        self.assertTemplateUsed(
            response, 'board/pages/labels_beneficiaries.html'
        )

    # Testing editing beneficiary type with good data
    def test_board_labels_beneficiaries_edit_type_correctly(self):
        self.client.post(
            reverse('home:index_auth'),
            data={
                'use_login': 'jane.doe@email.com',
                'use_password': '$Trong1234'
            },
            follow=True
        )
        response = self.client.post(
            reverse('board:labels_beneficiaries_edit'),
            data={
                'description': 'NewDescription',
                'edit_beneficiary': hash_gen(str(self.beneficiary.ben_slug)),
                'name': self.beneficiary.ben_name
            },
            follow=True
        )
        self.assertRedirects(
            response, reverse('board:labels_beneficiaries'), 302
        )
        self.assertNotIn('error', response.context.keys())
        self.assertIn('success', response.context.keys())
        self.assertIn('types', response.context.keys())
        self.assertIn('beneficiaries', response.context.keys())
        self.assertIn('filter', response.context.keys())
        self.assertIn('pages', response.context.keys())
        self.assertEqual(
            'NewDescription',
            response.context['types'][0].get('cat_description')
        )
        self.assertEqual(
            'Beneficiary type and name edited successfully.',
            response.context['success']
        )
        self.assertTemplateUsed(
            response, 'board/pages/labels_beneficiaries.html'
        )

    # Testing editing a system default beneficiary type
    def test_board_labels_beneficiaries_edit_default_type(self):
        self.client.post(
            reverse('home:index_auth'),
            data={
                'use_login': 'jane.doe@email.com',
                'use_password': '$Trong1234'
            },
            follow=True
        )

        category = self.make_beneficiary_category(
            user=None,
            cat_description='NewDescription',
            cat_slug='NewSlug'
        )

        beneficiary = self.make_beneficiary(
            user=User.objects.get(id=self.user.id),
            beneficiary_category=BeneficiaryCategory.objects.get(
                id=category.id
            ),
            ben_slug='DefaultSlug'
        )

        response = self.client.post(
            reverse('board:labels_beneficiaries_edit'),
            data={
                'description': 'EditDefault',
                'edit_beneficiary': hash_gen(str(beneficiary.ben_slug)),
                'name': beneficiary.ben_name
            },
            follow=True
        )
        self.assertRedirects(
            response, reverse('board:labels_beneficiaries'), 302
        )
        self.assertIn('error', response.context.keys())
        self.assertNotIn('success', response.context.keys())
        self.assertIn('types', response.context.keys())
        self.assertIn('beneficiaries', response.context.keys())
        self.assertIn('filter', response.context.keys())
        self.assertIn('pages', response.context.keys())
        self.assertEqual(
            'Invalid data, beneficiary type not edited:<br />Editing default types is prohibited.',  # noqa: E501
            response.context['error']
        )
        self.assertTemplateUsed(
            response, 'board/pages/labels_beneficiaries.html'
        )

    # Testing editing beneficiary type with good data and name with bad data
    def test_board_labels_beneficiaries_edit_type_correctly_name_bad_data(self):  # noqa: E501
        self.client.post(
            reverse('home:index_auth'),
            data={
                'use_login': 'jane.doe@email.com',
                'use_password': '$Trong1234'
            },
            follow=True
        )
        response = self.client.post(
            reverse('board:labels_beneficiaries_edit'),
            data={
                'description': 'NewDescription',
                'edit_beneficiary': hash_gen(str(self.beneficiary.ben_slug)),
                'name': 'NewName;'
            },
            follow=True
        )
        self.assertRedirects(
            response, reverse('board:labels_beneficiaries'), 302
        )
        self.assertNotIn('error', response.context.keys())
        self.assertIn('success', response.context.keys())
        self.assertIn('types', response.context.keys())
        self.assertIn('beneficiaries', response.context.keys())
        self.assertIn('filter', response.context.keys())
        self.assertIn('pages', response.context.keys())
        self.assertEqual(
            'NewDescription',
            response.context['types'][0].get('cat_description')
        )
        self.assertEqual(
            'Beneficiary type edited successfully.',
            response.context['success']
        )
        self.assertTemplateUsed(
            response, 'board/pages/labels_beneficiaries.html'
        )

    # Testing editing beneficiary type and name with good data
    def test_board_labels_beneficiaries_edit_type_name_correctly(self):
        self.client.post(
            reverse('home:index_auth'),
            data={
                'use_login': 'jane.doe@email.com',
                'use_password': '$Trong1234'
            },
            follow=True
        )
        response = self.client.post(
            reverse('board:labels_beneficiaries_edit'),
            data={
                'description': 'NewDescription',
                'edit_beneficiary': hash_gen(str(self.beneficiary.ben_slug)),
                'name': 'NewName'
            },
            follow=True
        )
        self.assertRedirects(
            response, reverse('board:labels_beneficiaries'), 302
        )
        self.assertNotIn('error', response.context.keys())
        self.assertIn('success', response.context.keys())
        self.assertIn('types', response.context.keys())
        self.assertIn('beneficiaries', response.context.keys())
        self.assertIn('filter', response.context.keys())
        self.assertIn('pages', response.context.keys())
        self.assertEqual(
            'NewDescription',
            response.context['types'][0].get('cat_description')
        )
        self.assertEqual(
            'Beneficiary type and name edited successfully.',
            response.context['success']
        )
        self.assertTemplateUsed(
            response, 'board/pages/labels_beneficiaries.html'
        )

    # Testing editing beneficiary name with bad data, empty and repeated
    @parameterized.expand([
        ('Beneficiary-other'),  # duplicated data
        (''),  # empty data
        (';;;;;'),  # invalid data
    ])
    def test_board_labels_beneficiaries_edit_name_errors(self, value):
        self.client.post(
            reverse('home:index_auth'),
            data={
                'use_login': 'jane.doe@email.com',
                'use_password': '$Trong1234'
            },
            follow=True
        )

        self.make_beneficiary(
            user=User.objects.get(id=self.user.id),
            beneficiary_category=BeneficiaryCategory.objects.get(
                id=self.category.id
            ),
            ben_name='Beneficiary-other',
            ben_slug='other'
        )

        response = self.client.post(
            reverse('board:labels_beneficiaries_edit'),
            data={
                'edit_beneficiary': hash_gen(str(self.beneficiary.ben_slug)),
                'name': value
            },
            follow=True
        )
        self.assertRedirects(
            response, reverse('board:labels_beneficiaries'), 302
        )
        self.assertIn('error', response.context.keys())
        self.assertNotIn('success', response.context.keys())
        self.assertIn('types', response.context.keys())
        self.assertIn('beneficiaries', response.context.keys())
        self.assertIn('filter', response.context.keys())
        self.assertIn('pages', response.context.keys())
        if value == 'Beneficiary-other':
            self.assertEqual(
                'Invalid data, beneficiary not edited:<br />This '
                'beneficiary is already register in our database and cannot be used.',  # noqa: E501
                response.context['error']
            )
        elif not value:
            self.assertEqual(
                'Invalid data, beneficiary not edited:<br />This field is required.',  # noqa: E501
                response.context['error']
            )
        else:
            self.assertEqual(
                'Invalid data, beneficiary not edited:<br />'
                'Entry cannot contain disallowed characters. e.g. &quot;;&quot;.',  # noqa: E501
                response.context['error']
            )
        self.assertTemplateUsed(
            response, 'board/pages/labels_beneficiaries.html'
        )

    # Testing deleting beneficiary name
    def test_board_labels_beneficiaries_delete_name(self):
        self.client.post(
            reverse('home:index_auth'),
            data={
                'use_login': 'jane.doe@email.com',
                'use_password': '$Trong1234'
            },
            follow=True
        )
        response = self.client.post(
            reverse('board:labels_beneficiaries_delete'),
            data={
                'del_beneficiary': hash_gen(str(self.beneficiary.ben_slug)),
            },
            follow=True
        )
        self.assertRedirects(
            response, reverse('board:labels_beneficiaries'), 302
        )
        self.assertNotIn('error', response.context.keys())
        self.assertIn('success', response.context.keys())
        self.assertIn('types', response.context.keys())
        self.assertTrue(response.context['types'])
        self.assertIn('beneficiaries', response.context.keys())
        self.assertFalse(response.context['beneficiaries'])
        self.assertIn('filter', response.context.keys())
        self.assertIn('pages', response.context.keys())
        self.assertEqual(
            'Beneficiary name removed successfully.',
            response.context['success']
        )
        self.assertTemplateUsed(
            response, 'board/pages/labels_beneficiaries.html'
        )
