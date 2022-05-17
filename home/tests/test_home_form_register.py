from unittest import TestCase

import pytest
from home.forms.resgiter_form import RegisterForm


@pytest.mark.fast
class TestHomeFormRegister(TestCase):
    # Testing received data from form
    def test_home_register_form_received_data(self):
        form = RegisterForm()
        self.assertIn('use_login', form.fields)
        self.assertIn('use_password', form.fields)
        self.assertNotIn('use_confirm_password', form.fields)
        self.assertNotIn('use_is_manager', form.fields)
        self.assertNotIn('use_is_valid', form.fields)
        self.assertNotIn('use_status', form.fields)
        self.assertNotIn('use_date_created', form.fields)
        self.assertNotIn('use_date_updated', form.fields)
        self.assertNotIn('use_date_deleted', form.fields)
