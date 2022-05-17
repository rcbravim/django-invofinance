from unittest.mock import patch

import pytest
from board.models import Country, State
from board.tests.test_board_helper import BoardHelperMixin
from board.views import labels_clients_view
from django.test import TestCase
from django.urls import resolve, reverse
from home.models import User
from home.tests.test_home_helper import HomeHelperMixin
from library.utils.auth import auth
from library.utils.helper import hash_gen
from parameterized import parameterized


@pytest.mark.fast
class TestBoardViewClients(TestCase, HomeHelperMixin, BoardHelperMixin):
    def setUp(self) -> None:
        self.user = self.make_user(use_is_valid=True)
        self.country = self.make_country()
        self.state = self.make_state(
            country=Country.objects.get(id=self.country.id)
        )
        self.client_label = self.make_client(
            user=User.objects.get(id=self.user.id),
            country=Country.objects.get(id=self.country.id),
            state=State.objects.get(id=self.state.id),
            cli_email='mail@email.com',
        )
        return super().setUp()

    # Testing the returned function on each view function
    def test_board_labels_clients_view_function(self):
        view = resolve(reverse('board:labels_clients'))
        self.assertIs(
            view.func.__module__,
            labels_clients_view.LabelsClientsView.__module__
        )

    def test_board_labels_clients_edit_view_function(self):
        view = resolve(reverse('board:labels_clients_edit'))
        self.assertIs(
            view.func.__module__,
            labels_clients_view.LabelsClientsView.__module__
        )

    def test_board_labels_clients_delete_view_function(self):
        view = resolve(reverse('board:labels_clients_delete'))
        self.assertIs(
            view.func.__module__,
            labels_clients_view.LabelsClientsView.__module__
        )

    # Testing wich template is loaded on
    # labels_clients view function

    # without credentials
    def test_board_labels_clients_no_credentials(self):
        response = self.client.get(
            reverse('board:labels_clients'),
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
    def test_board_labels_clients_with_credentials(self):
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
        response = self.client.get(reverse('board:labels_clients'))
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('error', response.context.keys())
        self.assertNotIn('success', response.context.keys())
        self.assertIn('countries', response.context.keys())
        self.assertIn('clients', response.context.keys())
        self.assertIn('filter', response.context.keys())
        self.assertIn('pages', response.context.keys())
        self.assertTemplateUsed(
            response, 'board/pages/labels_clients.html'
        )

    # testing pagination
    def test_board_labels_clients_pagination(self):
        self.client.post(
            reverse('home:index_auth'),
            data={
                'use_login': 'jane.doe@email.com',
                'use_password': '$Trong1234'
            },
            follow=True
        )

        for i in range(1, 100):
            self.make_client(
                user=User.objects.get(id=self.user.id),
                cli_name='Client' + str(i),
                cli_slug=i,
                country=Country.objects.get(id=self.country.id),
                state=State.objects.get(id=self.state.id),
            )

        with patch('board.views.labels_clients_view.PG_LIMIT', new=10):
            response = self.client.get(reverse('board:labels_clients'))
            self.assertEqual(
                response.context['pages']['pg_range'], [1, 2, 3, 4, 5]
            )

            response = self.client.get(
                reverse('board:labels_clients'),
                data={
                    'pg': 7
                }
            )
            self.assertEqual(
                response.context['pages']['pg_range'], [5, 6, 7, 8, 9]
            )
            self.assertEqual(response.context['pages']['total_pg'], 10)

            response = self.client.get(
                reverse('board:labels_clients'),
                data={
                    'pg': 10
                }
            )
            self.assertEqual(
                response.context['pages']['pg_range'], [6, 7, 8, 9, 10]
            )
            self.assertEqual(response.context['pages']['total_pg'], 10)

            response = self.client.get(
                reverse('board:labels_clients'),
                data={
                    'pg': 9
                }
            )
            self.assertEqual(
                response.context['pages']['pg_range'], [6, 7, 8, 9, 10]
            )
            self.assertEqual(response.context['pages']['total_pg'], 10)

    # testing filters
    def test_board_labels_clients_filters(self):
        self.client.post(
            reverse('home:index_auth'),
            data={
                'use_login': 'jane.doe@email.com',
                'use_password': '$Trong1234'
            },
            follow=True
        )

        country = self.make_country(
            cou_name='NewCountry'
        )
        state = self.make_state(
            country=Country.objects.get(id=country.id)
        )

        self.make_client(
            user=User.objects.get(id=self.user.id),
            cli_name='Client-other',
            cli_slug='other',
            country=Country.objects.get(id=country.id),
            state=State.objects.get(id=state.id),
        )

        for i in range(1, 100):
            self.make_client(
                user=User.objects.get(id=self.user.id),
                cli_name='Client' + str(i),
                cli_slug=i,
                country=Country.objects.get(id=self.country.id),
                state=State.objects.get(id=self.state.id),
            )

        with patch('board.views.labels_clients_view.PG_LIMIT', new=10):
            response = self.client.get(
                reverse('board:labels_clients'),
                data={
                    'country': hash_gen(str(country.id))
                }
            )

            self.assertEqual(response.context['pages']['pg_range'], [1])
            self.assertEqual(response.context['pages']['total_pg'], 1)
            self.assertEqual(len(response.context['clients']), 1)
            self.assertEqual(
                response.context['filter']['country'], hash_gen(str(country.id))  # noqa: E501
            )
            self.assertEqual(
                response.context['clients'][0]['cli_name'],
                'Client-other'
            )

            response = self.client.get(
                reverse('board:labels_clients'),
                data={
                    'search': '33'
                }
            )
            self.assertEqual(response.context['pages']['pg_range'], [1])
            self.assertEqual(response.context['pages']['total_pg'], 1)
            self.assertEqual(len(response.context['clients']), 1)
            self.assertEqual(response.context['filter']['search'], '33')
            self.assertEqual(
                response.context['clients'][0]['cli_name'],
                'Client33'
            )

            response = self.client.get(
                reverse('board:labels_clients'),
                data={
                    'search': 'Client',
                    'pg': 6
                }
            )
            self.assertEqual(
                response.context['pages']['pg_range'], [4, 5, 6, 7, 8]
            )
            self.assertEqual(response.context['pages']['total_pg'], 11)
            self.assertEqual(len(response.context['clients']), 10)
            self.assertEqual(
                response.context['filter']['search'], 'Client'
            )

            response = self.client.get(
                reverse('board:labels_clients'),
                data={
                    'search': 'Client',
                    'pg': 1
                }
            )
            self.assertEqual(
                response.context['pages']['pg_range'], [1, 2, 3, 4, 5]
            )
            self.assertEqual(response.context['pages']['total_pg'], 11)
            self.assertEqual(len(response.context['clients']), 10)
            self.assertEqual(
                response.context['filter']['search'], 'Client'
            )
            self.assertEqual(
                response.context['clients'][0]['cli_name'],
                'Client'
            )

            response = self.client.get(
                reverse('board:labels_clients'),
                data={
                    'search': 'nada'
                }
            )
            self.assertEqual(response.context['pages']['pg_range'], [])
            self.assertEqual(response.context['pages']['total_pg'], 0)
            self.assertEqual(len(response.context['clients']), 0)
            self.assertEqual(
                response.context['filter']['search'], 'nada'
            )

    # Testing editing client name with bad data, empty and repeated
    @parameterized.expand([
        ('Client-other'),  # duplicated data
        (''),  # empty data
        (';;;;;'),  # invalid data
    ])
    def test_board_labels_clients_edit_client_name_errors(self, value):
        self.client.post(
            reverse('home:index_auth'),
            data={
                'use_login': 'jane.doe@email.com',
                'use_password': '$Trong1234'
            },
            follow=True
        )

        self.make_client(
            user=User.objects.get(id=self.user.id),
            cli_name='Client-other',
            cli_slug='other',
            country=Country.objects.get(id=self.country.id),
            state=State.objects.get(id=self.state.id),
        )

        response = self.client.post(
            reverse('board:labels_clients_edit'),
            data={
                'client': value,
                'state': self.state.id,
                'country': hash_gen(str(self.country.id)),
                'city': 'City',
                'edit_client': hash_gen(self.client_label.cli_slug)
            },
            follow=True
        )
        self.assertRedirects(
            response, reverse('board:labels_clients'), 302
        )
        self.assertIn('error', response.context.keys())
        self.assertNotIn('success', response.context.keys())
        self.assertIn('countries', response.context.keys())
        self.assertIn('clients', response.context.keys())
        self.assertIn('filter', response.context.keys())
        self.assertIn('pages', response.context.keys())
        if value == 'Client-other':
            self.assertEqual(
                'Invalid data, client not edited:<br />This '
                'client is already register in our database and cannot be used.',  # noqa: E501
                response.context['error']
            )
        elif not value:
            self.assertEqual(
                'Invalid data, client not edited:<br />This field is required.',  # noqa: E501
                response.context['error']
            )
        else:
            self.assertEqual(
                'Invalid data, client not edited:<br />'
                'Entry cannot contain disallowed characters. e.g. &quot;;&quot;.',  # noqa: E501
                response.context['error']
            )
        self.assertTemplateUsed(
            response, 'board/pages/labels_clients.html'
        )

    # Testing editing client name with good data
    def test_board_labels_clients_edit_client_name_correctly(self):
        self.client.post(
            reverse('home:index_auth'),
            data={
                'use_login': 'jane.doe@email.com',
                'use_password': '$Trong1234'
            },
            follow=True
        )
        response = self.client.post(
            reverse('board:labels_clients_edit'),
            data={
                'client': 'ValidClient',
                'state': self.state.id,
                'country': hash_gen(str(self.country.id)),
                'city': 'City',
                'edit_client': hash_gen(self.client_label.cli_slug)
            },
            follow=True
        )
        self.assertRedirects(
            response, reverse('board:labels_clients'), 302
        )
        self.assertNotIn('error', response.context.keys())
        self.assertIn('success', response.context.keys())
        self.assertIn('countries', response.context.keys())
        self.assertIn('clients', response.context.keys())
        self.assertIn('filter', response.context.keys())
        self.assertIn('pages', response.context.keys())
        self.assertEqual(
            'ValidClient',
            response.context['clients'][0].get('cli_name')
        )
        self.assertEqual(
            'Client edited successfully.',
            response.context['success']
        )
        self.assertTemplateUsed(
            response, 'board/pages/labels_clients.html'
        )

    # Testing editing city with bad and empty data
    @parameterized.expand([
        (''),  # empty data
        (';;;;;'),  # invalid data
    ])
    def test_board_labels_clients_edit_city_errors(self, value):
        self.client.post(
            reverse('home:index_auth'),
            data={
                'use_login': 'jane.doe@email.com',
                'use_password': '$Trong1234'
            },
            follow=True
        )

        response = self.client.post(
            reverse('board:labels_clients_edit'),
            data={
                'client': 'Client',
                'state': self.state.id,
                'country': hash_gen(str(self.country.id)),
                'city': value,
                'edit_client': hash_gen(self.client_label.cli_slug)
            },
            follow=True
        )
        self.assertRedirects(
            response, reverse('board:labels_clients'), 302
        )
        self.assertIn('error', response.context.keys())
        self.assertNotIn('success', response.context.keys())
        self.assertIn('countries', response.context.keys())
        self.assertIn('clients', response.context.keys())
        self.assertIn('filter', response.context.keys())
        self.assertIn('pages', response.context.keys())
        if not value:
            self.assertEqual(
                'Invalid data, client not edited:<br />This field is required.',  # noqa: E501
                response.context['error']
            )
        else:
            self.assertEqual(
                'Invalid data, client not edited:<br />'
                'Entry cannot contain disallowed characters. e.g. &quot;;&quot;.',  # noqa: E501
                response.context['error']
            )
        self.assertTemplateUsed(
            response, 'board/pages/labels_clients.html'
        )

    # Testing editing city with good data
    def test_board_labels_clients_edit_city_correctly(self):
        self.client.post(
            reverse('home:index_auth'),
            data={
                'use_login': 'jane.doe@email.com',
                'use_password': '$Trong1234'
            },
            follow=True
        )
        response = self.client.post(
            reverse('board:labels_clients_edit'),
            data={
                'client': 'Client',
                'state': self.state.id,
                'country': hash_gen(str(self.country.id)),
                'city': 'ValidCity',
                'edit_client': hash_gen(self.client_label.cli_slug)
            },
            follow=True
        )
        self.assertRedirects(
            response, reverse('board:labels_clients'), 302
        )
        self.assertNotIn('error', response.context.keys())
        self.assertIn('success', response.context.keys())
        self.assertIn('countries', response.context.keys())
        self.assertIn('clients', response.context.keys())
        self.assertIn('filter', response.context.keys())
        self.assertIn('pages', response.context.keys())
        self.assertEqual(
            'Client edited successfully.',
            response.context['success']
        )
        self.assertTemplateUsed(
            response, 'board/pages/labels_clients.html'
        )

    # Testing editing email with bad and repeated data
    # empty data is not being tested here because email is not required
    @parameterized.expand([
        ('client@email.com'),  # duplicated data
        (';;;;;'),  # invalid data
        ('teste@'),  # invalid email
        ('teste@;;.com'),  # invalid email
    ])
    def test_board_labels_clients_edit_email_errors(self, value):
        self.client.post(
            reverse('home:index_auth'),
            data={
                'use_login': 'jane.doe@email.com',
                'use_password': '$Trong1234'
            },
            follow=True
        )

        self.make_client(
            user=User.objects.get(id=self.user.id),
            cli_name='Client-other',
            cli_slug='other',
            country=Country.objects.get(id=self.country.id),
            state=State.objects.get(id=self.state.id),
            cli_email='client@email.com'
        )

        response = self.client.post(
            reverse('board:labels_clients_edit'),
            data={
                'client': 'Client',
                'state': self.state.id,
                'country': hash_gen(str(self.country.id)),
                'city': 'City',
                'email': value,
                'edit_client': hash_gen(self.client_label.cli_slug)
            },
            follow=True
        )
        self.assertRedirects(
            response, reverse('board:labels_clients'), 302
        )
        self.assertIn('error', response.context.keys())
        self.assertNotIn('success', response.context.keys())
        self.assertIn('countries', response.context.keys())
        self.assertIn('clients', response.context.keys())
        self.assertIn('filter', response.context.keys())
        self.assertIn('pages', response.context.keys())
        if value == 'client@email.com':
            self.assertEqual(
                'Invalid data, client not edited:<br />'
                'This email is already register in our database and cannot be used.',  # noqa: E501
                response.context['error']
            )
        else:
            self.assertEqual(
                'Invalid data, client not edited:<br />'
                'Enter a valid email address.',
                response.context['error']
            )
        self.assertTemplateUsed(
            response, 'board/pages/labels_clients.html'
        )

    # Testing editing client name with good data
    def test_board_labels_clients_edit_email_correctly(self):
        self.client.post(
            reverse('home:index_auth'),
            data={
                'use_login': 'jane.doe@email.com',
                'use_password': '$Trong1234'
            },
            follow=True
        )

        self.make_client(
            user=User.objects.get(id=self.user.id),
            cli_name='Client-other',
            cli_slug='other',
            country=Country.objects.get(id=self.country.id),
            state=State.objects.get(id=self.state.id),
            cli_email='client@email.com'
        )

        response = self.client.post(
            reverse('board:labels_clients_edit'),
            data={
                'client': 'Client',
                'state': self.state.id,
                'country': hash_gen(str(self.country.id)),
                'city': 'ValidCity',
                'email': 'valid@email.com',
                'edit_client': hash_gen(self.client_label.cli_slug)
            },
            follow=True
        )
        self.assertRedirects(
            response, reverse('board:labels_clients'), 302
        )
        self.assertNotIn('error', response.context.keys())
        self.assertIn('success', response.context.keys())
        self.assertIn('countries', response.context.keys())
        self.assertIn('clients', response.context.keys())
        self.assertIn('filter', response.context.keys())
        self.assertIn('pages', response.context.keys())
        self.assertEqual(
            'Client edited successfully.',
            response.context['success']
        )
        self.assertTemplateUsed(
            response, 'board/pages/labels_clients.html'
        )

    # Testing adding phone with bad data
    # empty data is not being tested here because phone number is not required
    @parameterized.expand([
        (';;;;;'),  # invalid data
        ('teste@'),  # only string
        ('1234567'),  # only numbers but short
        ('123456789012'),  # only numbers but long
    ])
    def test_board_labels_clients_edit_phone_errors(self, value):
        self.client.post(
            reverse('home:index_auth'),
            data={
                'use_login': 'jane.doe@email.com',
                'use_password': '$Trong1234'
            },
            follow=True
        )
        response = self.client.post(
            reverse('board:labels_clients_edit'),
            data={
                'client': 'Client',
                'state': self.state.id,
                'country': hash_gen(str(self.country.id)),
                'city': 'City',
                'phone': value,
                'edit_client': hash_gen(self.client_label.cli_slug)
            },
            follow=True
        )
        self.assertRedirects(
            response, reverse('board:labels_clients'), 302
        )
        self.assertIn('error', response.context.keys())
        self.assertNotIn('success', response.context.keys())
        self.assertIn('countries', response.context.keys())
        self.assertIn('clients', response.context.keys())
        self.assertIn('filter', response.context.keys())
        self.assertIn('pages', response.context.keys())
        if ';' in value:
            self.assertEqual(
                'Invalid data, client not edited:<br />'
                'Entry cannot contain disallowed characters. e.g. &quot;;&quot;.',  # noqa: E501
                response.context['error']
            )
        else:
            self.assertEqual(
                'Invalid data, client not edited:<br />'
                'Invalid phone number.',
                response.context['error']
            )
        self.assertTemplateUsed(
            response, 'board/pages/labels_clients.html'
        )

    # Testing editing client name with good data
    def test_board_labels_clients_edit_phone_correctly(self):
        self.client.post(
            reverse('home:index_auth'),
            data={
                'use_login': 'jane.doe@email.com',
                'use_password': '$Trong1234'
            },
            follow=True
        )
        response = self.client.post(
            reverse('board:labels_clients_edit'),
            data={
                'client': 'Client',
                'state': self.state.id,
                'country': hash_gen(str(self.country.id)),
                'city': 'ValidCity',
                'phone': '1234567890',
                'edit_client': hash_gen(self.client_label.cli_slug)
            },
            follow=True
        )
        self.assertRedirects(
            response, reverse('board:labels_clients'), 302
        )
        self.assertNotIn('error', response.context.keys())
        self.assertIn('success', response.context.keys())
        self.assertIn('countries', response.context.keys())
        self.assertIn('clients', response.context.keys())
        self.assertIn('filter', response.context.keys())
        self.assertIn('pages', response.context.keys())
        self.assertEqual(
            'Client edited successfully.',
            response.context['success']
        )
        self.assertTemplateUsed(
            response, 'board/pages/labels_clients.html'
        )

    # Testing adding responsible with bad data
    # empty data is not being tested here because responsible is not required
    def test_board_labels_clients_edit_responsible_bad_data(self):
        self.client.post(
            reverse('home:index_auth'),
            data={
                'use_login': 'jane.doe@email.com',
                'use_password': '$Trong1234'
            },
            follow=True
        )
        response = self.client.post(
            reverse('board:labels_clients_edit'),
            data={
                'client': 'Client',
                'state': self.state.id,
                'country': hash_gen(str(self.country.id)),
                'city': 'City',
                'responsible': 'Jane Doe ;;;;;',
                'edit_client': hash_gen(self.client_label.cli_slug)
            },
            follow=True
        )
        self.assertRedirects(
            response, reverse('board:labels_clients'), 302
        )
        self.assertIn('error', response.context.keys())
        self.assertNotIn('success', response.context.keys())
        self.assertIn('countries', response.context.keys())
        self.assertIn('clients', response.context.keys())
        self.assertIn('filter', response.context.keys())
        self.assertIn('pages', response.context.keys())
        self.assertEqual(
            'Invalid data, client not edited:<br />'
            'Entry cannot contain disallowed characters. e.g. &quot;;&quot;.',
            response.context['error']
        )
        self.assertTemplateUsed(
            response, 'board/pages/labels_clients.html'
        )

    # Testing editing responsible with good data
    def test_board_labels_clients_edit_responsible_correctly(self):
        self.client.post(
            reverse('home:index_auth'),
            data={
                'use_login': 'jane.doe@email.com',
                'use_password': '$Trong1234'
            },
            follow=True
        )
        response = self.client.post(
            reverse('board:labels_clients_edit'),
            data={
                'client': 'Client',
                'state': self.state.id,
                'country': hash_gen(str(self.country.id)),
                'city': 'ValidCity',
                'responsible': 'Jane Doe',
                'edit_client': hash_gen(self.client_label.cli_slug)
            },
            follow=True
        )
        self.assertRedirects(
            response, reverse('board:labels_clients'), 302
        )
        self.assertNotIn('error', response.context.keys())
        self.assertIn('success', response.context.keys())
        self.assertIn('countries', response.context.keys())
        self.assertIn('clients', response.context.keys())
        self.assertIn('filter', response.context.keys())
        self.assertIn('pages', response.context.keys())
        self.assertEqual(
            'Client edited successfully.',
            response.context['success']
        )
        self.assertTemplateUsed(
            response, 'board/pages/labels_clients.html'
        )

    # Testing deleting client
    def test_board_labels_clients_delete_client(self):
        self.client.post(
            reverse('home:index_auth'),
            data={
                'use_login': 'jane.doe@email.com',
                'use_password': '$Trong1234'
            },
            follow=True
        )
        response = self.client.post(
            reverse('board:labels_clients_delete'),
            data={
                'del_client': hash_gen(self.client_label.cli_slug),
            },
            follow=True
        )
        self.assertRedirects(
            response, reverse('board:labels_clients'), 302
        )
        self.assertNotIn('error', response.context.keys())
        self.assertIn('success', response.context.keys())
        self.assertIn('countries', response.context.keys())
        self.assertFalse(response.context['countries'])
        self.assertIn('clients', response.context.keys())
        self.assertFalse(response.context['clients'])
        self.assertIn('filter', response.context.keys())
        self.assertIn('pages', response.context.keys())
        self.assertEqual(
            'Client removed successfully.',
            response.context['success']
        )
        self.assertTemplateUsed(
            response, 'board/pages/labels_clients.html'
        )
