from django.test import TestCase
from django.urls import reverse


class TestHomeURLs(TestCase):
    def test_home_index_url(self):
        self.assertEqual(reverse('home:index'), '/')

    def test_home_register_url(self):
        self.assertEqual(reverse('home:register'), '/register/')
