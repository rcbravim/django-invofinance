from unittest import TestCase

import pytest
from board.forms.profile_form import ProfileForm


@pytest.mark.fast
class TestBoardFormProfilePassword(TestCase):
    # Testing received data from form
    def test_board_profile_password_form_received_data(self):
        form = ProfileForm()
        self.assertIn('use_password', form.fields)
        self.assertNotIn('use_login', form.fields)
        self.assertNotIn('use_is_manager', form.fields)
        self.assertNotIn('use_is_valid', form.fields)
        self.assertNotIn('use_status', form.fields)
        self.assertNotIn('use_date_created', form.fields)
        self.assertNotIn('use_date_updated', form.fields)
        self.assertNotIn('use_date_deleted', form.fields)
