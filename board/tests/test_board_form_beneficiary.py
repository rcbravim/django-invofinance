from unittest import TestCase

import pytest
from board.forms.beneficiary_category_form import (BeneficiaryCategoryForm,
                                                   BeneficiaryForm)


@pytest.mark.fast
class TestBoardFormBeneficiary(TestCase):
    # Testing received data from form
    def test_board_beneficiary_form_received_data(self):
        form = BeneficiaryForm()
        self.assertIn('ben_name', form.fields)
        self.assertIn('user', form.fields)
        self.assertIn('beneficiary_category', form.fields)
        self.assertNotIn('ben_status', form.fields)
        self.assertNotIn('ben_date_created', form.fields)
        self.assertNotIn('ben_date_updated', form.fields)
        self.assertNotIn('ben_date_deleted', form.fields)

    def test_board_beneficiary_category_form_received_data(self):
        form = BeneficiaryCategoryForm()
        self.assertIn('cat_description', form.fields)
        self.assertIn('user', form.fields)
        self.assertNotIn('cat_status', form.fields)
        self.assertNotIn('cat_date_created', form.fields)
        self.assertNotIn('cat_date_updated', form.fields)
        self.assertNotIn('cat_date_deleted', form.fields)
