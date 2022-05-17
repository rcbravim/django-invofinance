from unittest.mock import patch

import pytest
from django.test import TestCase
from django.urls import resolve, reverse
from home.views import register_view
from parameterized import parameterized


@pytest.mark.fast
class TestHomeViewRegister(TestCase):
    def setUp(self) -> None:
        self.data = {
            'use_login': 'jane.doe@email.com',
            'use_password': '$Trong1234',
            'use_confirm_password': '$Trong1234'
        }
        return super().setUp()

    # Testing the returned function on each view function
    def test_home_register_view_function(self):
        view = resolve(reverse('home:register'))
        self.assertIs(
            view.func.__module__, register_view.RegisterView.__module__
        )

    def test_home_register_new_view_function(self):
        view = resolve(reverse('home:register_new'))
        self.assertIs(
            view.func.__module__, register_view.RegisterView.__module__
        )

    def test_home_register_verify_view_function(self):
        view = resolve(reverse('home:register_verify'))
        self.assertIs(
            view.func.__module__, register_view.RegisterView.__module__
        )

    def test_home_register_failed_view_function(self):
        view = resolve(reverse('home:register_failed'))
        self.assertIs(
            view.func.__module__, register_view.RegisterView.__module__
        )

    # Testing the returned status code on register view function
    def test_home_register_view_returned_status_code(self):
        response = self.client.get(reverse('home:register'))
        self.assertEqual(response.status_code, 200)

    # Testing wich template is loaded on register view function
    def test_home_register_view_template_load(self):
        response = self.client.get(reverse('home:register'))
        self.assertTemplateUsed(response, 'home/pages/register.html')

    # Testing all valid form data posted by client through the register form
    def test_home_register_new_view_post_all_valid_data(self):
        response = self.client.post(
            reverse('home:register_new'),
            data=self.data,
            follow=True
        )
        session = self.client.session
        self.assertIn('counter', session.keys())
        self.assertIn('email', session.keys())
        self.assertIn('password', session.keys())
        self.assertIn('stage', session.keys())
        self.assertEqual('two', session['stage'])
        self.assertRedirects(response, reverse('home:register'), 302)
        self.assertIn('attempts', response.context.keys())
        self.assertIn('email', response.context.keys())
        self.assertIn('stage', response.context.keys())
        self.assertEqual('jane.doe@email.com', response.context['email'])
        self.assertEqual('two', response.context['stage'])

    # Testing invalid or empty data posted by client through the register form
    @parameterized.expand([
        ('use_login', 'jane.doe'),  # invalid email
        ('use_login', ''),  # empty email
        ('use_password', '$TRONG1234'),  # no lowercase password
        ('use_password', '$trong1234'),  # no uppercase password
        ('use_password', '$TRongest'),  # no number password
        ('use_password', '$TRong1234;'),  # forbidden special char password
        ('use_password', '$To1234'),  # small password (less than 8 chars)
        ('use_password', ';;;;'),  # all wrong password
        ('use_password', ''),  # empty password
    ])
    def test_home_register_new_view_post_invalid_or_empty(self, field, value):
        self.data[field] = value
        if field == 'use_password':
            self.data['use_confirm_password'] = value
        response = self.client.post(
            reverse('home:register_new'),
            data=self.data
        )
        session = self.client.session
        self.assertIn('error', session.keys())
        self.assertRedirects(response, reverse('home:register'), 302, 200)

    # Testing different password data from its confirmation posted
    # by client through the register form
    def test_home_register_new_view_post_different_password(self):
        self.data['use_confirm_password'] = '$TRong1235'
        response = self.client.post(
            reverse('home:register_new'),
            data=self.data
        )
        session = self.client.session
        self.assertIn('error', session.keys())
        self.assertRedirects(response, reverse('home:register'), 302)

    # Testing empty password data posted by client through
    # the register form
    def test_home_register_new_view_post_empty_password(self):
        self.data['use_password'] = ''
        response = self.client.post(
            reverse('home:register_new'),
            data=self.data
        )
        session = self.client.session
        self.assertIn('error', session.keys())
        self.assertRedirects(response, reverse('home:register'), 302, 200)

    # Testing empty confirm_password data posted by client through
    # the register form
    def test_home_register_new_view_post_empty_confirm_password(self):
        self.data['use_confirm_password'] = ''
        response = self.client.post(
            reverse('home:register_new'),
            data=self.data
        )
        session = self.client.session
        self.assertIn('error', session.keys())
        self.assertRedirects(response, reverse('home:register'), 302, 200)

    # Testing existing email data posted by client through
    # the register form
    def test_home_register_new_view_post_existing_email(self):
        self.client.post(
            reverse('home:register_new'),
            data=self.data,
            follow=True
        )
        response = self.client.post(
            reverse('home:register_new'),
            data=self.data
        )
        session = self.client.session
        self.assertIn('error', session.keys())
        self.assertRedirects(response, reverse('home:register'), 302, 200)

    # Testing existing email-code
    def test_home_register_view_existing_email_code(self):
        session = self.client.session
        session.update({
            'stage': 'two',
            'counter': 1,
            'email': 'jane.doe@email.com',
            'password': '$TRong1234',
            'email-code': '1234'
        })
        session.save()
        self.client.get(reverse('home:register'))
        self.assertEqual('1234', session['email-code'])

    # Testing verification failure
    def test_home_register_verify_view_verification_failure(self):
        with patch('home.views.register_view.MAX_ATTEMPTS', new=3):
            session = self.client.session
            session.update({
                'stage': 'two',
                'counter': 1,
                'email': 'jane.doe@email.com',
                'password': '$TRong1234',
                'email-code': '1234'
            })
            session.save()
            response = self.client.post(
                reverse('home:register_verify'),
                data={
                    'digit1': '1',
                    'digit2': '1',
                    'digit3': '1',
                    'digit4': '1'
                },
                follow=True
            )
            self.assertEqual(2, response.context['attempts'])
            self.assertEqual('two', response.context['stage'])
            self.assertTemplateUsed(response, 'home/pages/register.html')

    # Testing verification failure - over the attempt limit
    def test_home_register_verify_view_verification_failure_over_attempt_limit(self):  # noqa: E501
        with patch('home.views.register_view.MAX_ATTEMPTS', new=3):
            self.client.post(
                reverse('home:register_new'),
                data=self.data,
                follow=True
            )
            session = self.client.session
            session.update({
                'counter': 3
            })
            session.save()
            response = self.client.post(
                reverse('home:register_verify'),
                data={
                    'digit1': '1',
                    'digit2': '1',
                    'digit3': '1',
                    'digit4': '1'
                },
                follow=True
            )
            self.assertRedirects(
                response, reverse('home:register_failed'), 302, 200
            )
            self.assertTemplateUsed(response, 'home/pages/failed.html')

    # Testing verification success
    def test_home_register_verify_view_verification_success(self):
        self.client.post(
            reverse('home:register_new'),
            data=self.data,
            follow=True
        )
        session = self.client.session
        session.update({
            'email-code': '1234'
        })
        session.save()
        response = self.client.post(
            reverse('home:register_verify'),
            data={
                'digit1': '1',
                'digit2': '2',
                'digit3': '3',
                'digit4': '4'
            },
            follow=True
        )
        self.assertRedirects(
            response, reverse('home:index'), 302, 200
        )
        self.assertTemplateUsed(response, 'home/pages/index.html')
        self.assertIn('success', response.context.keys())

    # Testing the access to register_failed without any session cache
    def test_home_register_failed_no_session(self):
        response = self.client.get(reverse('home:register_failed'))
        self.assertRedirects(response, reverse('home:404'), 302, 404)
