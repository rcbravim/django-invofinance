import re

import pytest
from board.views import profile_password_view
from django.test import TestCase
from django.urls import resolve, reverse
from home.tests.test_home_helper import HomeHelperMixin
from library.utils.auth import auth
from parameterized import parameterized


@pytest.mark.fast
class TestBoardViewProfile(TestCase, HomeHelperMixin):
    def setUp(self) -> None:
        self.user = self.make_user(use_is_valid=True)
        return super().setUp()

    # Testing the returned function on each view function
    def test_board_profile_view_function(self):
        view = resolve(reverse('board:password'))
        self.assertIs(
            view.func.__module__,
            profile_password_view.ProfilePasswordView.__module__
        )

    # Testing wich template is loaded on
    # profile view function

    # without credentials
    def test_board_profile_password_no_credentials(self):
        response = self.client.get(
            reverse('board:password'),
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
    def test_board_profile_password_with_credentials(self):
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
        response = self.client.get(reverse('board:password'), follow=True)
        self.assertRedirects(response, reverse('board:profile'), 302)
        self.assertIn('error', response.context.keys())
        self.assertNotIn('success', response.context.keys())
        self.assertEqual(
            'You are not authorized to access this page.',
            response.context['error']
        )
        self.assertTemplateUsed(
            response, 'board/pages/profile.html'
        )

    # Testing password with bad, short and empty password
    @parameterized.expand([
        ('$TRONG1234', '$TRONG1234'),  # no lowercase password
        ('$trong1234', '$trong1234'),  # no uppercase password
        ('$TRongest', '$TRongest'),  # no number password
        ('$TRong1234;', '$TRong1234;'),  # forbidden special char password
        ('$To1234', '$To1234'),  # small password (less than 8 chars)
        (';;;;', ';;;;'),  # all forbidden special password
        ('', ''),  # empty password
        ('$Trong1234', '$Trong1235'),  # different password
    ])
    def test_board_profile_password_view_invalid_password(self, password, password_confirmation):  # noqa: E501
        self.client.post(
            reverse('home:index_auth'),
            data={
                'use_login': 'jane.doe@email.com',
                'use_password': '$Trong1234'
            }
        )
        self.client.get(reverse('board:index'))
        self.client.post(
            reverse('board:profile'),
            data={
                'password': '$Trong1234'
            }
        )
        response = self.client.post(
            reverse('board:password'),
            data={
                'password': password,
                'password_confirmation': password_confirmation
            },
            follow=True
        )
        self.assertRedirects(response, reverse('board:password'), 302)
        self.assertIn('error', response.context.keys())
        self.assertNotIn('success', response.context.keys())
        self.assertTemplateUsed(response, 'board/pages/profile_password.html')
        self.assertEqual(2, self.client.session['password']['attempt'])
        if password == '$TRONG1234':
            self.assertEqual(
                'Invalid data, password not edited:<br />'
                'Password must contain at least ONE lowercase letter.',
                response.context['error']
            )
        elif password == '$trong1234':
            self.assertEqual(
                'Invalid data, password not edited:<br />'
                'Password must contain at least ONE capital letter.',
                response.context['error']
            )
        elif password == ';;;;':
            self.assertEqual(
                'Invalid data, password not edited:<br />'
                'Password must contain at least ONE number.<br />'
                'Password must contain at least ONE capital letter.<br />'
                'Password must contain at least ONE lowercase letter.<br />'
                'Password must contain at least 8 characters.<br />Password '
                'cannot contain disallowed characters. e.g. &quot;;&quot;.',
                response.context['error']
            )
        elif password and not bool(re.search(r'\d', password)):
            self.assertEqual(
                'Invalid data, password not edited:<br />'
                'Password must contain at least ONE number.',
                response.context['error']
            )
        elif ';' in password:
            self.assertEqual(
                'Invalid data, password not edited:<br />'
                'Password cannot contain disallowed characters. e.g. &quot;;&quot;.',  # noqa: E501
                response.context['error']
            )
        elif password and len(password) < 8:
            self.assertEqual(
                'Invalid data, password not edited:<br />'
                'Password must contain at least 8 characters.',
                response.context['error']
            )
        elif not password:
            self.assertEqual(
                'Invalid data, password not edited:<br />'
                'Password field is required.',
                response.context['error']
            )
        else:
            self.assertEqual(
                'Invalid data, password not edited:<br />'
                'The password and its confirmation are not the same.',
                response.context['error']
            )

    # Testing invalid attempt more than 3 times
    def test_board_profile_password_view_invalid_password_more_than_3_times(self):  # noqa: E501
        self.client.post(
            reverse('home:index_auth'),
            data={
                'use_login': 'jane.doe@email.com',
                'use_password': '$Trong1234'
            }
        )
        self.client.get(reverse('board:index'))
        self.client.post(
            reverse('board:profile'),
            data={
                'password': '$Trong1234'
            }
        )
        for i in range(2):
            self.client.post(
                reverse('board:password'),
                data={
                    'password': 'password',
                    'password_confirmation': 'password_confirmation'
                }
            )
        response = self.client.post(
            reverse('board:password'),
            data={
                'password': 'password',
                'password_confirmation': 'password_confirmation'
            },
            follow=True
        )
        self.assertRedirects(response, reverse('board:profile'), 302)
        self.assertIn('session', response.context.keys())
        self.assertIn('error', response.context.keys())
        self.assertNotIn('success', response.context.keys())
        self.assertNotIn('password', self.client.session)
        self.assertTemplateUsed(response, 'board/pages/profile.html')
        self.assertEqual(
            'You have reached the maximum number of attempts, please log in and try again.',  # noqa: E501
            response.context['error']
        )

    # Testing change password correctly
    def test_board_profile_password_view_correct_password(self):
        self.client.post(
            reverse('home:index_auth'),
            data={
                'use_login': 'jane.doe@email.com',
                'use_password': '$Trong1234'
            }
        )
        self.client.get(reverse('board:index'))
        self.client.post(
            reverse('board:profile'),
            data={
                'password': '$Trong1234'
            }
        )
        response = self.client.post(
            reverse('board:password'),
            data={
                'password': '$Trong4321',
                'password_confirmation': '$Trong4321'
            },
            follow=True
        )
        self.assertRedirects(response, reverse('board:profile'), 302)
        self.assertIn('session', response.context.keys())
        self.assertNotIn('error', response.context.keys())
        self.assertIn('success', response.context.keys())
        self.assertNotIn('password', self.client.session)
        self.assertTemplateUsed(response, 'board/pages/profile.html')
        self.assertEqual(
            'Password edited successfully.',
            response.context['success']
        )
