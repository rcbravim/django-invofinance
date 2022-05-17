import pytest
from board.models import Country, State
from board.tests.test_board_helper import BoardHelperMixin
from board.views import labels_clients_form_view
from django.test import TestCase
from django.urls import resolve, reverse
from home.models import User
from home.tests.test_home_helper import HomeHelperMixin
from library.utils.auth import auth
from library.utils.helper import hash_gen
from parameterized import parameterized


@pytest.mark.fast
class TestBoardViewClientsForm(TestCase, HomeHelperMixin, BoardHelperMixin):
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
    def test_board_labels_clients_form_view_function(self):
        view = resolve(reverse('board:labels_clients_form'))
        self.assertIs(
            view.func.__module__,
            labels_clients_form_view.LabelsClientsFormView.__module__
        )

    def test_board_labels_clients_form_new_view_function(self):
        view = resolve(reverse('board:labels_clients_form_new'))
        self.assertIs(
            view.func.__module__,
            labels_clients_form_view.LabelsClientsFormView.__module__
        )

    # Testing wich template is loaded on
    # labels_clients_form view function

    # without credentials
    def test_board_labels_clients_form_no_credentials(self):
        response = self.client.get(
            reverse('board:labels_clients_form'),
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
    def test_board_labels_clients_form_with_credentials(self):
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
        response = self.client.get(reverse('board:labels_clients_form'))
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('error', response.context.keys())
        self.assertNotIn('success', response.context.keys())
        self.assertIn('countries', response.context.keys())
        self.assertTemplateUsed(
            response, 'board/pages/labels_clients_form.html'
        )

    # Testing adding client name with bad data, empty and repeated
    @parameterized.expand([
        ('Client'),  # duplicated data
        (''),  # empty data
        (';;;;;'),  # invalid data
    ])
    def test_board_labels_clients_form_new_client_errors(self, value):
        self.client.post(
            reverse('home:index_auth'),
            data={
                'use_login': 'jane.doe@email.com',
                'use_password': '$Trong1234'
            },
            follow=True
        )
        response = self.client.post(
            reverse('board:labels_clients_form_new'),
            data={
                'client': value,
                'state': self.state.id,
                'city': 'Any City',
                'country': hash_gen(str(self.country.id)),
            },
            follow=True
        )
        self.assertRedirects(
            response, reverse('board:labels_clients_form'), 302
        )
        self.assertIn('error', response.context.keys())
        self.assertNotIn('success', response.context.keys())
        self.assertIn('countries', response.context.keys())
        if value == 'Client':
            self.assertEqual(
                'Invalid data, client not registered:<br />This '
                'client is already register in our database and cannot be used.',  # noqa: E501
                response.context['error']
            )
        elif not value:
            self.assertEqual(
                'Invalid data, client not registered:<br />'
                'This field is required.',
                response.context['error']
            )
        else:
            self.assertEqual(
                'Invalid data, client not registered:<br />'
                'Entry cannot contain disallowed characters. e.g. &quot;;&quot;.',  # noqa: E501
                response.context['error']
            )
        self.assertTemplateUsed(
            response, 'board/pages/labels_clients_form.html'
        )

    # Testing adding new client
    def test_board_labels_clients_form_new_adding_new_client(self):
        self.client.post(
            reverse('home:index_auth'),
            data={
                'use_login': 'jane.doe@email.com',
                'use_password': '$Trong1234'
            },
            follow=True
        )
        response = self.client.post(
            reverse('board:labels_clients_form_new'),
            data={
                'client': 'New Client',
                'state': self.state.id,
                'city': 'Any City',
                'country': hash_gen(str(self.country.id)),
            },
            follow=True
        )
        self.assertRedirects(
            response, reverse('board:labels_clients_form'), 302
        )
        self.assertIn('success', response.context.keys())
        self.assertEqual(
            'Client added successfully.', response.context['success']
        )
        self.assertTemplateUsed(
            response, 'board/pages/labels_clients_form.html'
        )

    # Testing adding city with bad data and empty
    @parameterized.expand([
        (''),  # empty data
        (';;;;;'),  # invalid data
    ])
    def test_board_labels_clients_form_new_city_errors(self, value):
        self.client.post(
            reverse('home:index_auth'),
            data={
                'use_login': 'jane.doe@email.com',
                'use_password': '$Trong1234'
            },
            follow=True
        )
        response = self.client.post(
            reverse('board:labels_clients_form_new'),
            data={
                'client': 'New Client',
                'state': self.state.id,
                'city': value,
                'country': hash_gen(str(self.country.id)),
            },
            follow=True
        )
        self.assertRedirects(
            response, reverse('board:labels_clients_form'), 302
        )
        self.assertIn('error', response.context.keys())
        self.assertNotIn('success', response.context.keys())
        self.assertIn('countries', response.context.keys())
        self.assertTemplateUsed(
            response, 'board/pages/labels_clients_form.html'
        )

        if not value:
            if not value:
                self.assertEqual(
                    'Invalid data, client not registered:<br />'
                    'This field is required.',
                    response.context['error']
                )
        else:
            self.assertEqual(
                'Invalid data, client not registered:<br />'
                'Entry cannot contain disallowed characters. e.g. &quot;;&quot;.',  # noqa: E501
                response.context['error']
            )

    # Testing adding e-mail with bad data and repeated
    # empty data is not being tested here because email is not required
    @parameterized.expand([
        ('mail@email.com'),  # duplicated data
        (';;;;;'),  # invalid data
        ('teste@'),  # invalid email
        ('teste@;;.com'),  # invalid email
    ])
    def test_board_labels_clients_form_new_email_errors(self, value):
        self.client.post(
            reverse('home:index_auth'),
            data={
                'use_login': 'jane.doe@email.com',
                'use_password': '$Trong1234'
            },
            follow=True
        )
        response = self.client.post(
            reverse('board:labels_clients_form_new'),
            data={
                'client': 'New Client',
                'state': self.state.id,
                'city': 'Any City',
                'country': hash_gen(str(self.country.id)),
                'email': value
            },
            follow=True
        )
        self.assertRedirects(
            response, reverse('board:labels_clients_form'), 302
        )
        self.assertIn('error', response.context.keys())
        self.assertNotIn('success', response.context.keys())
        self.assertIn('countries', response.context.keys())
        self.assertTemplateUsed(
            response, 'board/pages/labels_clients_form.html'
        )

        if value == 'mail@email.com':
            self.assertEqual(
                'Invalid data, client not registered:<br />'
                'This email is already register in our database and cannot be used.',  # noqa: E501
                response.context['error']
            )
        else:
            self.assertEqual(
                'Invalid data, client not registered:<br />'
                'Enter a valid email address.',
                response.context['error']
            )

    # Testing adding phone with bad data
    # empty data is not being tested here because phone number is not required
    @parameterized.expand([
        (';;;;;'),  # invalid data
        ('teste@'),  # only string
        ('1234567'),  # only numbers but short
        ('123456789012'),  # only numbers but long
    ])
    def test_board_labels_clients_form_new_phone_errors(self, value):
        self.client.post(
            reverse('home:index_auth'),
            data={
                'use_login': 'jane.doe@email.com',
                'use_password': '$Trong1234'
            },
            follow=True
        )
        response = self.client.post(
            reverse('board:labels_clients_form_new'),
            data={
                'client': 'New Client',
                'state': self.state.id,
                'city': 'Any City',
                'country': hash_gen(str(self.country.id)),
                'phone': value
            },
            follow=True
        )
        self.assertRedirects(
            response, reverse('board:labels_clients_form'), 302
        )
        self.assertIn('error', response.context.keys())
        self.assertNotIn('success', response.context.keys())
        self.assertIn('countries', response.context.keys())
        self.assertTemplateUsed(
            response, 'board/pages/labels_clients_form.html'
        )
        if ';' in value:
            self.assertEqual(
                'Invalid data, client not registered:<br />'
                'Entry cannot contain disallowed characters. e.g. &quot;;&quot;.',  # noqa: E501
                response.context['error']
            )
        else:
            self.assertEqual(
                'Invalid data, client not registered:<br />'
                'Invalid phone number.',
                response.context['error']
            )

    # Testing adding responsible with bad data
    # empty data is not being tested here because responsible is not required
    def test_board_labels_clients_form_new_responsible_bad_data(self):
        self.client.post(
            reverse('home:index_auth'),
            data={
                'use_login': 'jane.doe@email.com',
                'use_password': '$Trong1234'
            },
            follow=True
        )
        response = self.client.post(
            reverse('board:labels_clients_form_new'),
            data={
                'client': 'New Client',
                'state': self.state.id,
                'city': 'Any City',
                'country': hash_gen(str(self.country.id)),
                'responsible': 'Jane Doe ;;;;;'
            },
            follow=True
        )
        self.assertRedirects(
            response, reverse('board:labels_clients_form'), 302
        )
        self.assertIn('error', response.context.keys())
        self.assertNotIn('success', response.context.keys())
        self.assertIn('countries', response.context.keys())
        self.assertTemplateUsed(
            response, 'board/pages/labels_clients_form.html'
        )
        self.assertEqual(
            'Invalid data, client not registered:<br />'
            'Entry cannot contain disallowed characters. e.g. &quot;;&quot;.',
            response.context['error']
        )
