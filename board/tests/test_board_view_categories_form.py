import pytest
from board.models import Category
from board.tests.test_board_helper import BoardHelperMixin
from board.views import labels_categories_form_view
from django.test import TestCase
from django.urls import resolve, reverse
from home.models import User
from home.tests.test_home_helper import HomeHelperMixin
from library.utils.auth import auth
from library.utils.helper import hash_gen
from parameterized import parameterized


@pytest.mark.fast
class TestBoardViewCategoriesForm(TestCase, HomeHelperMixin,
                                  BoardHelperMixin):
    def setUp(self) -> None:
        self.user = self.make_user(use_is_valid=True)
        self.category = self.make_category(
            user=User.objects.get(id=self.user.id)
        )
        self.subcategory = self.make_subcategory(
            category=Category.objects.get(id=self.category.id)
        )
        return super().setUp()

    # Testing the returned function on each view function
    def test_board_labels_categories_form_view_function(self):
        view = resolve(reverse('board:labels_categories_form'))
        self.assertIs(
            view.func.__module__,
            labels_categories_form_view.LabelsCategoriesFormView.__module__
        )

    def test_board_labels_categories_form_new_view_function(self):
        view = resolve(reverse('board:labels_categories_form'))
        self.assertIs(
            view.func.__module__,
            labels_categories_form_view.LabelsCategoriesFormView.__module__
        )

    def test_board_labels_categories_form_delete_type_view_function(self):
        view = resolve(reverse('board:labels_categories_form'))
        self.assertIs(
            view.func.__module__,
            labels_categories_form_view.LabelsCategoriesFormView.__module__
        )

    # Testing wich template is loaded on
    # labels_categories_form view function

    # without credentials
    def test_board_labels_categories_form_no_credentials(self):
        response = self.client.get(
            reverse('board:labels_categories_form'),
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
    def test_board_labels_categories_form_with_credentials(self):
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
        response = self.client.get(reverse('board:labels_categories_form'))
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('error', response.context.keys())
        self.assertNotIn('success', response.context.keys())
        self.assertIn('categories', response.context.keys())
        self.assertTemplateUsed(
            response, 'board/pages/labels_categories_form.html'
        )

    # Testing deleting category type
    def test_board_labels_categories_form_delete_category(self):
        self.client.post(
            reverse('home:index_auth'),
            data={
                'use_login': 'jane.doe@email.com',
                'use_password': '$Trong1234'
            },
            follow=True
        )
        response = self.client.post(
            reverse('board:labels_categories_form_delete_category'),
            data={'name': hash_gen(self.category.cat_slug)},
            follow=True
        )
        self.assertRedirects(
            response, reverse('board:labels_categories_form'), 302
        )
        self.assertIn('success', response.context.keys())
        self.assertNotIn('error', response.context.keys())
        self.assertEqual(
            'Category removed successfully.',
            response.context['success']
        )
        self.assertIn('categories', response.context.keys())
        self.assertNotIn('Category', response.context['categories'])
        self.assertFalse(response.context['categories'])
        self.assertTemplateUsed(
            response, 'board/pages/labels_categories_form.html'
        )

    # Testing adding category type with bad data, empty and repeated
    @parameterized.expand([
        ('Category'),  # duplicated data
        (''),  # empty data
        (';;;;;'),  # invalid data
    ])
    def test_board_labels_categories_form_new_type_errors(self, value):
        self.client.post(
            reverse('home:index_auth'),
            data={
                'use_login': 'jane.doe@email.com',
                'use_password': '$Trong1234'
            },
            follow=True
        )
        response = self.client.post(
            reverse('board:labels_categories_form_new'),
            data={
                'outer-group[0][name]': value,
                'outer-group[0][inlineRadioOptions]': 1
            },
            follow=True
        )
        self.assertRedirects(
            response, reverse('board:labels_categories_form'), 302
        )
        self.assertIn('error', response.context.keys())
        self.assertNotIn('success', response.context.keys())
        self.assertIn('categories', response.context.keys())
        if value == 'Category':
            self.assertEqual(
                'Invalid data, category not registered:<br />This '
                'category is already register in our database and cannot be used.',  # noqa: E501
                response.context['error']
            )
        elif not value:
            self.assertEqual(
                'Invalid data, category not registered:<br />This field is required.',  # noqa: E501
                response.context['error']
            )
        else:
            self.assertEqual(
                'Invalid data, category not registered:<br />'
                'Entry cannot contain disallowed characters. e.g. &quot;;&quot;.',  # noqa: E501
                response.context['error']
            )
        self.assertTemplateUsed(
            response, 'board/pages/labels_categories_form.html'
        )

    # Testing adding new category
    def test_board_labels_categories_form_new_adding_new_category(self):
        self.client.post(
            reverse('home:index_auth'),
            data={
                'use_login': 'jane.doe@email.com',
                'use_password': '$Trong1234'
            },
            follow=True
        )
        response = self.client.post(
            reverse('board:labels_categories_form_new'),
            data={
                'outer-group[0][name]': 'NewCategory',
                'outer-group[0][inlineRadioOptions]': 1
            },
            follow=True
        )
        self.assertRedirects(
            response, reverse('board:labels_categories_form'), 302
        )
        self.assertIn('success', response.context.keys())
        self.assertIn('categories', response.context.keys())
        self.assertEqual(
            'Category added successfully.', response.context['success']
        )
        self.assertTemplateUsed(
            response, 'board/pages/labels_categories_form.html'
        )

    # Testing adding new category and subcategories
    def test_board_labels_categories_form_new_adding_category_and_subcategory(self):  # noqa: E501
        self.client.post(
            reverse('home:index_auth'),
            data={
                'use_login': 'jane.doe@email.com',
                'use_password': '$Trong1234'
            },
            follow=True
        )
        response = self.client.post(
            reverse('board:labels_categories_form_new'),
            data={
                'outer-group[0][name]': 'NewCategory',
                'outer-group[0][inlineRadioOptions]': 1,
                'outer-group[0][inner-group][0][subname]': 'Subname1',
                'outer-group[0][inner-group][1][subname]': 'Subname2',
            },
            follow=True
        )
        self.assertRedirects(
            response, reverse('board:labels_categories_form'), 302
        )
        self.assertIn('success', response.context.keys())
        self.assertIn('categories', response.context.keys())
        self.assertEqual(
            'Category and subcategory(ies) added successfully.',
            response.context['success']
        )
        self.assertTemplateUsed(
            response, 'board/pages/labels_categories_form.html'
        )

    # Testing adding subcategories with existing category
    def test_board_labels_categories_form_new_adding_subcategory_with_existing_category(self):  # noqa: E501
        self.client.post(
            reverse('home:index_auth'),
            data={
                'use_login': 'jane.doe@email.com',
                'use_password': '$Trong1234'
            },
            follow=True
        )
        response = self.client.post(
            reverse('board:labels_categories_form_new'),
            data={
                'outer-group[0][name]': hash_gen(self.category.cat_slug),
                'outer-group[0][inner-group][0][subname]': 'Subname1',
                'outer-group[0][inner-group][1][subname]': 'Subname2',
            },
            follow=True
        )
        self.assertRedirects(
            response, reverse('board:labels_categories_form'), 302
        )
        self.assertIn('success', response.context.keys())
        self.assertNotIn('error', response.context.keys())
        self.assertIn('categories', response.context.keys())
        self.assertEqual(
            'Subcategory(ies) added successfully.',
            response.context['success']
        )
        self.assertTemplateUsed(
            response, 'board/pages/labels_categories_form.html'
        )

    # Testing adding identical subcategories with existing category
    def test_board_labels_categories_form_new_adding_identical_subcategories_with_existing_category(self):  # noqa: E501
        self.client.post(
            reverse('home:index_auth'),
            data={
                'use_login': 'jane.doe@email.com',
                'use_password': '$Trong1234'
            },
            follow=True
        )
        response = self.client.post(
            reverse('board:labels_categories_form_new'),
            data={
                'outer-group[0][name]': hash_gen(self.category.cat_slug),
                'outer-group[0][inner-group][0][subname]': 'Subname1',
                'outer-group[0][inner-group][1][subname]': 'Subname1',
            },
            follow=True
        )
        self.assertRedirects(
            response, reverse('board:labels_categories_form'), 302
        )
        self.assertIn('success', response.context.keys())
        self.assertNotIn('error', response.context.keys())
        self.assertIn('categories', response.context.keys())
        self.assertEqual(
            'Subcategory(ies) added successfully.',
            response.context['success']
        )
        self.assertTemplateUsed(
            response, 'board/pages/labels_categories_form.html'
        )

    # Testing adding no subcategories with existing category
    def test_board_labels_categories_form_new_no_subcategories_with_existing_category(self):  # noqa: E501
        self.client.post(
            reverse('home:index_auth'),
            data={
                'use_login': 'jane.doe@email.com',
                'use_password': '$Trong1234'
            },
            follow=True
        )
        response = self.client.post(
            reverse('board:labels_categories_form_new'),
            data={
                'outer-group[0][name]': hash_gen(self.category.cat_slug),
            },
            follow=True
        )
        self.assertRedirects(
            response, reverse('board:labels_categories_form'), 302
        )
        self.assertNotIn('success', response.context.keys())
        self.assertIn('error', response.context.keys())
        self.assertIn('categories', response.context.keys())
        self.assertEqual(
            'Invalid data! You must add at least one subcategory when using an existing category.',  # noqa: E501
            response.context['error']
        )
        self.assertTemplateUsed(
            response, 'board/pages/labels_categories_form.html'
        )

    # Testing adding subcategory with bad data, empty and repeated
    @parameterized.expand([
        ('Subcategory'),  # duplicated data
        (''),  # empty data
        (';;;;;'),  # invalid data
    ])
    def test_board_labels_categories_form_new_errors(self, value):
        self.client.post(
            reverse('home:index_auth'),
            data={
                'use_login': 'jane.doe@email.com',
                'use_password': '$Trong1234'
            },
            follow=True
        )
        response = self.client.post(
            reverse('board:labels_categories_form_new'),
            data={
                'outer-group[0][name]': hash_gen(self.category.cat_slug),
                'outer-group[0][inner-group][0][subname]': value,
            },
            follow=True
        )
        self.assertRedirects(
            response, reverse('board:labels_categories_form'), 302
        )
        self.assertIn('error', response.context.keys())
        self.assertNotIn('success', response.context.keys())
        self.assertIn('categories', response.context.keys())
        self.assertTemplateUsed(
            response, 'board/pages/labels_categories_form.html'
        )

        if value == 'Subcategory':
            self.assertEqual(
                'Invalid data, subcategory not registered:<br />This '
                'subcategory is already register in our database and cannot be used.',  # noqa: E501
                response.context['error']
            )
        elif not value:
            if not value:
                self.assertEqual(
                    'Invalid data, subcategory not registered:<br />This field is required.',  # noqa: E501
                    response.context['error']
                )
        else:
            self.assertEqual(
                'Invalid data, subcategory not registered:<br />'
                'Entry cannot contain disallowed characters. e.g. &quot;;&quot;.',  # noqa: E501
                response.context['error']
            )
