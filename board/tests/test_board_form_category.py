from unittest import TestCase

import pytest
from board.forms.category_form import CategoryForm, SubCategoryForm


@pytest.mark.fast
class TestBoardFormCategory(TestCase):
    # Testing received data from form
    def test_board_category_form_received_data(self):
        form = CategoryForm()
        self.assertIn('user', form.fields)
        self.assertIn('cat_name', form.fields)
        self.assertIn('cat_type', form.fields)
        self.assertNotIn('cat_slug', form.fields)
        self.assertNotIn('cat_status', form.fields)
        self.assertNotIn('cat_date_created', form.fields)
        self.assertNotIn('cat_date_updated', form.fields)
        self.assertNotIn('cat_date_deleted', form.fields)

    def test_board_subcategory_form_received_data(self):
        form = SubCategoryForm()
        self.assertIn('category', form.fields)
        self.assertIn('sub_name', form.fields)
        self.assertNotIn('sub_slug', form.fields)
        self.assertNotIn('sub_status', form.fields)
        self.assertNotIn('sub_date_created', form.fields)
        self.assertNotIn('sub_date_updated', form.fields)
        self.assertNotIn('sub_date_deleted', form.fields)
