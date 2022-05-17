from unittest import TestCase

import pytest
from board.forms.client_form import ClientForm


@pytest.mark.fast
class TestBoardFormClient(TestCase):
    # Testing received data from form
    def test_board_client_form_received_data(self):
        form = ClientForm()
        self.assertIn('user', form.fields)
        self.assertIn('cli_name', form.fields)
        self.assertIn('country', form.fields)
        self.assertIn('state', form.fields)
        self.assertIn('cli_city', form.fields)
        self.assertIn('cli_email', form.fields)
        self.assertIn('cli_phone', form.fields)
        self.assertIn('cli_responsible', form.fields)
        self.assertNotIn('cli_status', form.fields)
        self.assertNotIn('cli_date_created', form.fields)
        self.assertNotIn('cli_date_updated', form.fields)
        self.assertNotIn('cli_date_deleted', form.fields)
