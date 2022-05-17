from unittest import TestCase

import pytest
from board.forms.index_form import AnalyticForm, IndexForm


@pytest.mark.fast
class TestBoardFormIndex(TestCase):
    # Testing received data from form
    def test_board_index_form_received_data(self):
        form = IndexForm()
        self.assertIn('user', form.fields)
        self.assertIn('rel_entry_date', form.fields)
        self.assertIn('rel_description', form.fields)
        self.assertIn('rel_gen_status', form.fields)
        self.assertIn('rel_amount', form.fields)
        self.assertNotIn('rel_status', form.fields)
        self.assertNotIn('rel_date_created', form.fields)
        self.assertNotIn('rel_date_updated', form.fields)
        self.assertNotIn('rel_date_deleted', form.fields)

    def test_board_analytic_form_received_data(self):
        form = AnalyticForm()
        self.assertIn('user', form.fields)
        self.assertIn('ana_cycle', form.fields)
        self.assertIn('ana_json', form.fields)
        self.assertNotIn('ana_status', form.fields)
        self.assertNotIn('ana_date_created', form.fields)
        self.assertNotIn('ana_date_updated', form.fields)
        self.assertNotIn('ana_date_deleted', form.fields)
