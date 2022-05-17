from unittest import TestCase

import pytest
from home.forms.index_form import IndexForm


@pytest.mark.fast
class TestHomeFormIndex(TestCase):
    # Testing received data from form
    def test_home_index_form_received_data(self):
        form = IndexForm()
        self.assertIn('use_login', form.fields)
        self.assertIn('use_password', form.fields)
        self.assertNotIn('use_confirm_password', form.fields)
        self.assertNotIn('use_is_manager', form.fields)
        self.assertNotIn('use_is_valid', form.fields)
        self.assertNotIn('use_status', form.fields)
        self.assertNotIn('use_date_created', form.fields)
        self.assertNotIn('use_date_updated', form.fields)
        self.assertNotIn('use_date_deleted', form.fields)
