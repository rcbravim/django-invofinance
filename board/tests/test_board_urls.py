import pytest
from django.test import TestCase
from django.urls import reverse


@pytest.mark.fast
class TestBoardURLs(TestCase):
    # Testing if the URL tag is pointing to the correct location

    # INDEX
    def test_board_index_url(self):
        self.assertEqual(reverse('board:index'), '/board/')

    def test_board_index_new_url(self):
        self.assertEqual(reverse('board:index_new'), '/board/index/new/')

    def test_board_index_edit_url(self):
        self.assertEqual(reverse('board:index_edit'), '/board/index/edit/')

    def test_board_index_delete_url(self):
        self.assertEqual(reverse('board:index_delete'), '/board/index/delete/')

    # LABELS/BENEFICIARIES
    def test_board_labels_beneficiaries_url(self):
        self.assertEqual(
            reverse('board:labels_beneficiaries'),
            '/board/labels/beneficiaries/'
        )

    def test_board_labels_beneficiaries_edit_url(self):
        self.assertEqual(
            reverse('board:labels_beneficiaries_edit'),
            '/board/labels/beneficiaries/edit/'
        )

    def test_board_labels_beneficiaries_delete_url(self):
        self.assertEqual(
            reverse('board:labels_beneficiaries_delete'),
            '/board/labels/beneficiaries/delete/'
        )

    # LABELS/BENEFICIARIES/FORM
    def test_board_labels_beneficiaries_form_url(self):
        self.assertEqual(
            reverse('board:labels_beneficiaries_form'),
            '/board/labels/beneficiaries/form/'
        )

    def test_board_labels_beneficiaries_form_new_url(self):
        self.assertEqual(
            reverse('board:labels_beneficiaries_form_new'),
            '/board/labels/beneficiaries/form/new/'
        )

    def test_board_labels_beneficiaries_form_delete_type_url(self):
        self.assertEqual(
            reverse('board:labels_beneficiaries_form_delete_type'),
            '/board/labels/beneficiaries/form/delete/type/'
        )

    # LABELS/CATEGORIES
    def test_board_labels_categories_url(self):
        self.assertEqual(
            reverse('board:labels_categories'),
            '/board/labels/categories/'
        )

    def test_board_labels_categories_edit_url(self):
        self.assertEqual(
            reverse('board:labels_categories_edit'),
            '/board/labels/categories/edit/'
        )

    def test_board_labels_categories_delete_url(self):
        self.assertEqual(
            reverse('board:labels_categories_delete'),
            '/board/labels/categories/delete/'
        )

    # LABELS/CATEGORIES/FORM
    def test_board_labels_categories_form_url(self):
        self.assertEqual(
            reverse('board:labels_categories_form'),
            '/board/labels/categories/form/'
        )

    def test_board_labels_categories_form_new_url(self):
        self.assertEqual(
            reverse('board:labels_categories_form_new'),
            '/board/labels/categories/form/new/'
        )

    def test_board_labels_categories_form_delete_category_url(self):
        self.assertEqual(
            reverse('board:labels_categories_form_delete_category'),
            '/board/labels/categories/form/delete/category/'
        )

    # LABELS/CLIENTS
    def test_board_labels_clients_url(self):
        self.assertEqual(
            reverse('board:labels_clients'),
            '/board/labels/clients/'
        )

    def test_board_labels_clients_edit_url(self):
        self.assertEqual(
            reverse('board:labels_clients_edit'),
            '/board/labels/clients/edit/'
        )

    def test_board_labels_clients_delete_url(self):
        self.assertEqual(
            reverse('board:labels_clients_delete'),
            '/board/labels/clients/delete/'
        )

    # LABELS/CLIENTS/FORM
    def test_board_labels_clients_form_url(self):
        self.assertEqual(
            reverse('board:labels_clients_form'),
            '/board/labels/clients/form/'
        )

    def test_board_labels_clients_form_new_url(self):
        self.assertEqual(
            reverse('board:labels_clients_form_new'),
            '/board/labels/clients/form/new/'
        )

    # LABELS/FINANCIAL
    def test_board_labels_financial_url(self):
        self.assertEqual(
            reverse('board:labels_financial'),
            '/board/labels/financial/'
        )

    def test_board_labels_financial_edit_url(self):
        self.assertEqual(
            reverse('board:labels_financial_edit'),
            '/board/labels/financial/edit/'
        )

    def test_board_labels_financial_delete_url(self):
        self.assertEqual(
            reverse('board:labels_financial_delete'),
            '/board/labels/financial/delete/'
        )

    # LABELS/FINANCIAL/FORM
    def test_board_labels_financial_form_url(self):
        self.assertEqual(
            reverse('board:labels_financial_form'),
            '/board/labels/financial/form/'
        )

    def test_board_labels_financial_form_new_url(self):
        self.assertEqual(
            reverse('board:labels_financial_form_new'),
            '/board/labels/financial/form/new/'
        )

    # PROFILE
    def test_board_profile_url(self):
        self.assertEqual(
            reverse('board:profile'),
            '/board/profile/'
        )

    # PROFILE/PASSWORD/CHANGE
    def test_board_profile_password_change_url(self):
        self.assertEqual(
            reverse('board:password'),
            '/board/profile/password/change/'
        )

    # 404
    def test_board_404_url(self):
        self.assertEqual(reverse('board:404'), '/board/404/')
