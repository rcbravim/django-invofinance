from unittest import TestCase

import pytest
from board.forms.financial_form import FinancialForm


@pytest.mark.fast
class TestBoardFormFinancial(TestCase):
    # Testing received data from form
    def test_board_financial_form_received_data(self):
        form = FinancialForm()
        self.assertIn('user', form.fields)
        self.assertIn('fin_cost_center', form.fields)
        self.assertIn('fin_description', form.fields)
        self.assertIn('fin_bank_name', form.fields)
        self.assertIn('fin_bank_branch', form.fields)
        self.assertIn('fin_bank_account', form.fields)
        self.assertIn('fin_type', form.fields)
        self.assertNotIn('fin_status', form.fields)
        self.assertNotIn('fin_date_created', form.fields)
        self.assertNotIn('fin_date_updated', form.fields)
        self.assertNotIn('fin_date_deleted', form.fields)
