import pytest
from board.views import profile_view
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
        view = resolve(reverse('board:profile'))
        self.assertIs(
            view.func.__module__,
            profile_view.ProfileView.__module__
        )

    # Testing wich template is loaded on
    # profile view function

    # without credentials
    def test_board_profile_no_credentials(self):
        response = self.client.get(
            reverse('board:profile'),
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
    def test_board_profile_with_credentials(self):
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
        response = self.client.get(reverse('board:profile'))
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('error', response.context.keys())
        self.assertNotIn('success', response.context.keys())
        self.assertTemplateUsed(
            response, 'board/pages/profile.html'
        )

    # Testing password with bad, short and wrong password
    @parameterized.expand([
        ('CostCenter'),  # wrong password
        (';;;;;'),  # invalid password
        ('$T1234'),  # short password
    ])
    def test_board_profile_view_invalid_password(self, value):
        self.client.post(
            reverse('home:index_auth'),
            data={
                'use_login': 'jane.doe@email.com',
                'use_password': '$Trong1234'
            }
        )
        self.client.get(reverse('board:index'))
        response = self.client.post(
            reverse('board:profile'),
            data={
                'password': value
            },
            follow=True
        )
        self.assertRedirects(response, reverse('board:profile'), 302)
        self.assertIn('error', response.context.keys())
        self.assertNotIn('success', response.context.keys())
        self.assertTemplateUsed(response, 'board/pages/profile.html')
        if ';' in value:
            self.assertEqual('Invalid password.', response.context['error'])
        else:
            self.assertEqual('Incorrect password.', response.context['error'])

    # Testing password correctly
    def test_board_profile_view_correct_password(self):
        self.client.post(
            reverse('home:index_auth'),
            data={
                'use_login': 'jane.doe@email.com',
                'use_password': '$Trong1234'
            }
        )
        self.client.get(reverse('board:index'))
        response = self.client.post(
            reverse('board:profile'),
            data={
                'password': '$Trong1234'
            },
            follow=True
        )
        self.assertRedirects(response, reverse('board:password'), 302)
        self.assertNotIn('error', response.context.keys())
        self.assertNotIn('success', response.context.keys())
        self.assertTemplateUsed(response, 'board/pages/profile_password.html')
