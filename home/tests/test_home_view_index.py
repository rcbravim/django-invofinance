import pytest
from django.test import TestCase
from django.urls import resolve, reverse
from home.models import User
from home.tests.test_home_helper import HomeHelperMixin
from home.views import index_view
from library.utils.auth import auth, credentials


@pytest.mark.fast
class TestHomeViewIndex(TestCase, HomeHelperMixin):
    def setUp(self) -> None:
        self.data = {
            'use_login': 'jane.doe@email.com',
            'use_password': '$Trong1234',
            'use_confirm_password': '$Trong1234'
        }
        return super().setUp()

    # Testing the returned function on each view function
    def test_home_index_view_function(self):
        view = resolve(reverse('home:index'))
        self.assertIs(
            view.func.__module__, index_view.IndexView.__module__
        )

    def test_home_index_nd_view_function(self):
        view = resolve('/index/')
        self.assertIs(
            view.func.__module__, index_view.IndexView.__module__
        )

    def test_home_index_auth_view_function(self):
        view = resolve(reverse('home:index_auth'))
        self.assertIs(
            view.func.__module__, index_view.IndexView.__module__
        )

    # Testing the returned status code on each view function
    def test_home_index_view_returned_status_code(self):
        response = self.client.get(reverse('home:index'))
        self.assertEqual(response.status_code, 200)

    def test_home_index_nd_view_returned_status_code(self):
        response = self.client.get('/index/')
        self.assertEqual(response.status_code, 200)

    def test_home_index_auth_view_returned_status_code(self):
        response = self.client.get(reverse('home:index_auth'))
        self.assertEqual(response.status_code, 200)

    # Testing wich template is loaded on each view function
    def test_home_index_view_template_load(self):
        response = self.client.get(reverse('home:index'))
        self.assertTemplateUsed(response, 'home/pages/index.html')

    def test_home_index_nd_view_template_load(self):
        response = self.client.get('/index/')
        self.assertTemplateUsed(response, 'home/pages/index.html')

    # Not verified user try to login
    def test_home_index_auth_view_not_verified_user_loggin_in(self):
        self.client.post(
            reverse('home:register_new'),
            data=self.data,
            follow=True
        )
        del self.data['use_confirm_password']
        response = self.client.post(
            reverse('home:index_auth'),
            data=self.data,
            follow=True
        )
        session = self.client.session
        self.assertIn('counter', session.keys())
        self.assertIn('email', session.keys())
        self.assertIn('password', session.keys())
        self.assertIn('stage', session.keys())
        self.assertIn('email-code', session.keys())
        self.assertEqual('two', session['stage'])
        self.assertRedirects(response, reverse('home:register'), 302, 200)
        self.assertIn('attempts', response.context.keys())
        self.assertIn('email', response.context.keys())
        self.assertIn('stage', response.context.keys())
        self.assertIn('modal', response.context.keys())
        self.assertEqual('jane.doe@email.com', response.context['email'])
        self.assertEqual('two', response.context['stage'])

    # Not verified user try to login - without session cache
    def test_home_index_auth_view_not_verified_user_loggin_in_without_session_cache(self):  # noqa: E501
        self.make_user()
        del self.data['use_confirm_password']
        response = self.client.post(
            reverse('home:index_auth'),
            data=self.data
        )
        session = self.client.session
        self.assertIn('counter', session.keys())
        self.assertIn('email', session.keys())
        self.assertIn('password', session.keys())
        self.assertIn('stage', session.keys())
        self.assertNotIn('email-code', session.keys())
        self.assertIn('modal', session.keys())
        self.assertEqual('two', session['stage'])
        self.assertRedirects(response, reverse('home:register'), 302, 200)

    # Verified user loggin in
    def test_home_index_auth_view_verified_user_loggin_in(self):
        self.client.post(
            reverse('home:register_new'),
            data=self.data,
            follow=True
        )

        user = User.objects.all()[0]
        user.use_is_valid = True
        user.save()

        del self.data['use_confirm_password']
        response = self.client.post(
            reverse('home:index_auth'),
            data=self.data,
            follow=True
        )
        session = self.client.session
        self.assertIn('auth', session.keys())
        self.assertEqual(
            'jane.doe@email.com',
            credentials(session['auth'], 'login')
        )
        self.assertRedirects(response, reverse('board:index'), 302, 200)
        self.assertIn('success', response.context.keys())

    # Testing invalid email argument
    def test_home_index_auth_view_invalid_email_args(self):
        response = self.client.post(
            reverse('home:index_auth'),
            data={
                'use_login': 'jane.doe@email',
                'use_password': '$TRong1234'
            }
        )
        session = self.client.session
        self.assertIn('error', session.keys())
        self.assertRedirects(response, reverse('home:index'), 302, 200)

    # Testing invalid password argument
    def test_home_index_auth_view_invalid_password_args(self):
        response = self.client.post(
            reverse('home:index_auth'),
            data={
                'use_login': 'jane.doe@email.com',
                'use_password': '$TRong1234;;'
            }
        )
        session = self.client.session
        self.assertIn('error', session.keys())
        self.assertRedirects(response, reverse('home:index'), 302, 200)

    # Testing going to home:index with auth credentials
    def test_home_index_with_credentials(self):
        payload = {
            'whoami': 1,
            'login': 'jane.doe@email.com',
            'manager': False
        }
        session = self.client.session
        session.update({
            'auth': auth(payload)
        })
        session.save()
        response = self.client.get(reverse('home:index'), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home/pages/index.html')
        self.assertNotIn('auth', self.client.session.keys())
