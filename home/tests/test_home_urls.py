import pytest
from django.test import TestCase
from django.urls import reverse


@pytest.mark.fast
class TestHomeURLs(TestCase):
    # Testing if the URL tag is pointing to the correct location

    # INDEX
    def test_home_index_url(self):
        self.assertEqual(reverse('home:index'), '/')

    def test_home_index_auth_url(self):
        self.assertEqual(reverse('home:index_auth'), '/index/auth/')

    # 404
    def test_home_404_url(self):
        self.assertEqual(reverse('home:404'), '/404/')

    # 500
    def test_home_500_url(self):
        self.assertEqual(reverse('home:500'), '/500/')

    # REGISTER
    def test_home_register_url(self):
        self.assertEqual(reverse('home:register'), '/register/')

    def test_home_register_new_url(self):
        self.assertEqual(reverse('home:register_new'), '/register/new/')

    def test_home_register_verify_url(self):
        self.assertEqual(reverse('home:register_verify'), '/register/verify/')

    def test_home_register_failed_url(self):
        self.assertEqual(reverse('home:register_failed'), '/register/failed/')
