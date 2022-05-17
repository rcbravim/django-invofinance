from unittest.mock import patch

import pytest
from board.models import Category
from board.tests.test_board_helper import BoardHelperMixin
from board.views import labels_categories_view
from django.test import TestCase
from django.urls import resolve, reverse
from home.models import User
from home.tests.test_home_helper import HomeHelperMixin
from library.utils.auth import auth
from library.utils.helper import hash_gen
from parameterized import parameterized


@pytest.mark.fast
class TestBoardViewCategories(TestCase, HomeHelperMixin, BoardHelperMixin):
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
    def test_board_labels_categories_view_function(self):
        view = resolve(reverse('board:labels_categories'))
        self.assertIs(
            view.func.__module__,
            labels_categories_view.LabelsCategoriesView.__module__
        )

    def test_board_labels_categories_edit_view_function(self):
        view = resolve(reverse('board:labels_categories_edit'))
        self.assertIs(
            view.func.__module__,
            labels_categories_view.LabelsCategoriesView.__module__
        )

    def test_board_labels_categories_delete_view_function(self):
        view = resolve(reverse('board:labels_categories_delete'))
        self.assertIs(
            view.func.__module__,
            labels_categories_view.LabelsCategoriesView.__module__
        )

    # Testing wich template is loaded on
    # labels_categories view function

    # without credentials
    def test_board_labels_categories_no_credentials(self):
        response = self.client.get(
            reverse('board:labels_categories'),
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
    def test_board_labels_categories_with_credentials(self):
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
        response = self.client.get(reverse('board:labels_categories'))
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('error', response.context.keys())
        self.assertNotIn('success', response.context.keys())
        self.assertIn('categories', response.context.keys())
        self.assertIn('labels', response.context.keys())
        self.assertIn('filter', response.context.keys())
        self.assertIn('pages', response.context.keys())
        self.assertTemplateUsed(
            response, 'board/pages/labels_categories.html'
        )

    # testing pagination
    def test_board_labels_categories_pagination(self):
        self.client.post(
            reverse('home:index_auth'),
            data={
                'use_login': 'jane.doe@email.com',
                'use_password': '$Trong1234'
            },
            follow=True
        )

        for i in range(1, 100):
            self.make_subcategory(
                category=Category.objects.get(id=self.category.id),
                sub_name='SubCategory' + str(i),
                sub_slug=i,
            )

        with patch('board.views.labels_categories_view.PG_LIMIT', new=10):
            response = self.client.get(reverse('board:labels_categories'))
            self.assertEqual(
                response.context['pages']['pg_range'], [1, 2, 3, 4, 5]
            )

            response = self.client.get(
                reverse('board:labels_categories'),
                data={
                    'pg': 7
                }
            )
            self.assertEqual(
                response.context['pages']['pg_range'], [5, 6, 7, 8, 9]
            )
            self.assertEqual(response.context['pages']['total_pg'], 10)

            response = self.client.get(
                reverse('board:labels_categories'),
                data={
                    'pg': 10
                }
            )
            self.assertEqual(
                response.context['pages']['pg_range'], [6, 7, 8, 9, 10]
            )
            self.assertEqual(response.context['pages']['total_pg'], 10)

            response = self.client.get(
                reverse('board:labels_categories'),
                data={
                    'pg': 9
                }
            )
            self.assertEqual(
                response.context['pages']['pg_range'], [6, 7, 8, 9, 10]
            )
            self.assertEqual(response.context['pages']['total_pg'], 10)

    # testing filters
    def test_board_labels_categories_filters(self):
        self.client.post(
            reverse('home:index_auth'),
            data={
                'use_login': 'jane.doe@email.com',
                'use_password': '$Trong1234'
            },
            follow=True
        )

        category = self.make_category(
            user=User.objects.get(id=self.user.id),
            cat_slug=10,
        )

        self.make_subcategory(
            category=Category.objects.get(id=category.id),
            sub_name='SubCategory-other',
            sub_slug='other',
        )

        for i in range(1, 100):
            self.make_subcategory(
                category=Category.objects.get(id=self.category.id),
                sub_name='SubCategory' + str(i),
                sub_slug=i,
            )

        with patch('board.views.labels_categories_view.PG_LIMIT', new=10):
            response = self.client.get(
                reverse('board:labels_categories'),
                data={
                    'label': hash_gen('10')
                }
            )

            self.assertEqual(response.context['pages']['pg_range'], [1])
            self.assertEqual(response.context['pages']['total_pg'], 1)
            self.assertEqual(len(response.context['categories']), 1)
            self.assertEqual(
                response.context['filter']['label'], hash_gen(str(10))
            )
            self.assertEqual(
                response.context['categories'][0]['subcategory__sub_name'],
                'SubCategory-other'
            )

            response = self.client.get(
                reverse('board:labels_categories'),
                data={
                    'search': '33'
                }
            )
            self.assertEqual(response.context['pages']['pg_range'], [1])
            self.assertEqual(response.context['pages']['total_pg'], 1)
            self.assertEqual(len(response.context['categories']), 1)
            self.assertEqual(response.context['filter']['search'], '33')
            self.assertEqual(
                response.context['categories'][0]['subcategory__sub_name'],
                'SubCategory33'
            )

            response = self.client.get(
                reverse('board:labels_categories'),
                data={
                    'search': 'SubCategory',
                    'pg': 6
                }
            )
            self.assertEqual(
                response.context['pages']['pg_range'], [4, 5, 6, 7, 8]
            )
            self.assertEqual(response.context['pages']['total_pg'], 11)
            self.assertEqual(len(response.context['categories']), 10)
            self.assertEqual(
                response.context['filter']['search'], 'SubCategory'
            )

            response = self.client.get(
                reverse('board:labels_categories'),
                data={
                    'search': 'SubCategory',
                    'pg': 1
                }
            )
            self.assertEqual(
                response.context['pages']['pg_range'], [1, 2, 3, 4, 5]
            )
            self.assertEqual(response.context['pages']['total_pg'], 11)
            self.assertEqual(len(response.context['categories']), 10)
            self.assertEqual(
                response.context['filter']['search'], 'SubCategory'
            )
            self.assertEqual(
                response.context['categories'][1]['subcategory__sub_name'],
                'SubCategory-other'
            )

            response = self.client.get(
                reverse('board:labels_categories'),
                data={
                    'search': 'nada'
                }
            )
            self.assertEqual(response.context['pages']['pg_range'], [])
            self.assertEqual(response.context['pages']['total_pg'], 0)
            self.assertEqual(len(response.context['categories']), 0)
            self.assertEqual(
                response.context['filter']['search'], 'nada'
            )

            response = self.client.get(
                reverse('board:labels_categories'),
                data={
                    'type': '2'
                }
            )
            self.assertEqual(response.context['pages']['pg_range'], [])
            self.assertEqual(response.context['pages']['total_pg'], 0)
            self.assertEqual(len(response.context['categories']), 0)
            self.assertEqual(
                response.context['filter']['type'], '2'
            )

    # Testing editing category with bad data, empty and repeated
    @parameterized.expand([
        ('Category-other'),  # duplicated data
        (''),  # empty data
        (';;;;;'),  # invalid data
    ])
    def test_board_labels_categories_edit_type_errors(self, value):
        self.client.post(
            reverse('home:index_auth'),
            data={
                'use_login': 'jane.doe@email.com',
                'use_password': '$Trong1234'
            },
            follow=True
        )

        self.make_category(
            user=User.objects.get(id=self.user.id),
            cat_name='Category-other',
            cat_slug='other'
        )

        response = self.client.post(
            reverse('board:labels_categories_edit'),
            data={
                'name': value,
                'edit_category': hash_gen(str(self.subcategory.sub_slug)),
                'inlineRadio': self.category.cat_type,
                'subname': self.subcategory.sub_name
            },
            follow=True
        )
        self.assertRedirects(
            response, reverse('board:labels_categories'), 302
        )
        self.assertIn('error', response.context.keys())
        self.assertNotIn('success', response.context.keys())
        self.assertIn('labels', response.context.keys())
        self.assertIn('categories', response.context.keys())
        self.assertIn('filter', response.context.keys())
        self.assertIn('pages', response.context.keys())
        if value == 'Category-other':
            self.assertEqual(
                'Invalid data, category name not edited:<br />This '
                'category is already register in our database and cannot be used.',  # noqa: E501
                response.context['error']
            )
        elif not value:
            self.assertEqual(
                'Invalid data, category name not edited:<br />This field is required.',  # noqa: E501
                response.context['error']
            )
        else:
            self.assertEqual(
                'Invalid data, category name not edited:<br />'
                'Entry cannot contain disallowed characters. e.g. &quot;;&quot;.',  # noqa: E501
                response.context['error']
            )
        self.assertTemplateUsed(
            response, 'board/pages/labels_categories.html'
        )

    # Testing editing category type with good data
    def test_board_labels_categories_edit_type_correctly(self):
        self.client.post(
            reverse('home:index_auth'),
            data={
                'use_login': 'jane.doe@email.com',
                'use_password': '$Trong1234'
            },
            follow=True
        )
        response = self.client.post(
            reverse('board:labels_categories_edit'),
            data={
                'name': 'ValidCategory',
                'edit_category': hash_gen(str(self.subcategory.sub_slug)),
                'inlineRadio': self.category.cat_type,
                'subname': self.subcategory.sub_name
            },
            follow=True
        )
        self.assertRedirects(
            response, reverse('board:labels_categories'), 302
        )
        self.assertNotIn('error', response.context.keys())
        self.assertIn('success', response.context.keys())
        self.assertIn('labels', response.context.keys())
        self.assertIn('categories', response.context.keys())
        self.assertIn('filter', response.context.keys())
        self.assertIn('pages', response.context.keys())
        self.assertEqual(
            'ValidCategory',
            response.context['categories'][0].get('cat_name')
        )
        self.assertEqual(
            'Category and subcategory edited successfully.',
            response.context['success']
        )
        self.assertTemplateUsed(
            response, 'board/pages/labels_categories.html'
        )

    # Testing editing category with good data and subcategory with bad data
    def test_board_labels_categories_edit_type_correctly_name_error(self):
        self.client.post(
            reverse('home:index_auth'),
            data={
                'use_login': 'jane.doe@email.com',
                'use_password': '$Trong1234'
            },
            follow=True
        )
        response = self.client.post(
            reverse('board:labels_categories_edit'),
            data={
                'name': 'ValidCategory',
                'edit_category': hash_gen(str(self.subcategory.sub_slug)),
                'inlineRadio': self.category.cat_type,
                'subname': 'ValidSubCategory;'
            },
            follow=True
        )
        self.assertRedirects(
            response, reverse('board:labels_categories'), 302
        )
        self.assertNotIn('error', response.context.keys())
        self.assertIn('success', response.context.keys())
        self.assertIn('labels', response.context.keys())
        self.assertIn('categories', response.context.keys())
        self.assertIn('filter', response.context.keys())
        self.assertIn('pages', response.context.keys())
        self.assertEqual(
            'ValidCategory',
            response.context['labels'][0].get('cat_name')
        )
        self.assertEqual(
            'Category edited successfully.',
            response.context['success']
        )
        self.assertTemplateUsed(
            response, 'board/pages/labels_categories.html'
        )

    # Testing editing category and subcategory with good data
    def test_board_labels_categories_edit_type_name_correctly(self):
        self.client.post(
            reverse('home:index_auth'),
            data={
                'use_login': 'jane.doe@email.com',
                'use_password': '$Trong1234'
            },
            follow=True
        )
        response = self.client.post(
            reverse('board:labels_categories_edit'),
            data={
                'name': 'ValidCategory',
                'edit_category': hash_gen(str(self.subcategory.sub_slug)),
                'inlineRadio': self.category.cat_type,
                'subname': 'ValidSubCategory'
            },
            follow=True
        )
        self.assertRedirects(
            response, reverse('board:labels_categories'), 302
        )
        self.assertNotIn('error', response.context.keys())
        self.assertIn('success', response.context.keys())
        self.assertIn('labels', response.context.keys())
        self.assertIn('categories', response.context.keys())
        self.assertIn('filter', response.context.keys())
        self.assertIn('pages', response.context.keys())
        self.assertEqual(
            'ValidCategory',
            response.context['labels'][0].get('cat_name')
        )
        self.assertEqual(
            'Category and subcategory edited successfully.',
            response.context['success']
        )
        self.assertTemplateUsed(
            response, 'board/pages/labels_categories.html'
        )

    # Testing editing subcategory with bad data, empty and repeated
    @parameterized.expand([
        ('Subcategory-other'),  # duplicated data
        (''),  # empty data
        (';;;;;'),  # invalid data
    ])
    def test_board_labels_categories_edit_name_errors(self, value):
        self.client.post(
            reverse('home:index_auth'),
            data={
                'use_login': 'jane.doe@email.com',
                'use_password': '$Trong1234'
            },
            follow=True
        )

        self.make_subcategory(
            category=Category.objects.get(id=self.category.id),
            sub_name='Subcategory-other',
            sub_slug='other'
        )

        response = self.client.post(
            reverse('board:labels_categories_edit'),
            data={
                'edit_category': hash_gen(str(self.subcategory.sub_slug)),
                'subname': value
            },
            follow=True
        )
        self.assertRedirects(
            response, reverse('board:labels_categories'), 302
        )
        self.assertIn('error', response.context.keys())
        self.assertNotIn('success', response.context.keys())
        self.assertIn('labels', response.context.keys())
        self.assertIn('categories', response.context.keys())
        self.assertIn('filter', response.context.keys())
        self.assertIn('pages', response.context.keys())
        if value == 'Subcategory-other':
            self.assertEqual(
                'Invalid data, subcategory not edited:<br />This '
                'subcategory is already register in our database and cannot be used.',  # noqa: E501
                response.context['error']
            )
        elif not value:
            self.assertEqual(
                'Invalid data, subcategory not edited:<br />This field is required.',  # noqa: E501
                response.context['error']
            )
        else:
            self.assertEqual(
                'Invalid data, subcategory not edited:<br />'
                'Entry cannot contain disallowed characters. e.g. &quot;;&quot;.',  # noqa: E501
                response.context['error']
            )
        self.assertTemplateUsed(
            response, 'board/pages/labels_categories.html'
        )

    # Testing deleting subcategory
    def test_board_labels_categories_delete_subcategory(self):
        self.client.post(
            reverse('home:index_auth'),
            data={
                'use_login': 'jane.doe@email.com',
                'use_password': '$Trong1234'
            },
            follow=True
        )
        response = self.client.post(
            reverse('board:labels_categories_delete'),
            data={
                'del_subcategory': hash_gen(str(self.subcategory.sub_slug)),
            },
            follow=True
        )
        self.assertRedirects(
            response, reverse('board:labels_categories'), 302
        )
        self.assertNotIn('error', response.context.keys())
        self.assertIn('success', response.context.keys())
        self.assertIn('labels', response.context.keys())
        self.assertTrue(response.context['labels'])
        self.assertIn('categories', response.context.keys())
        self.assertFalse(response.context['categories'])
        self.assertIn('filter', response.context.keys())
        self.assertIn('pages', response.context.keys())
        self.assertEqual(
            'Subcategory removed successfully.',
            response.context['success']
        )
        self.assertTemplateUsed(
            response, 'board/pages/labels_categories.html'
        )
