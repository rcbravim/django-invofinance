import pytest
from django.test import TestCase
from django.urls import resolve, reverse
from home.views import error_view


@pytest.mark.fast
class TestHomeViewHandler404(TestCase):
    # Testing the returned function on each view function
    def test_home_handler404_view_function(self):
        view = resolve(reverse('home:404'))
        self.assertIs(view.func, error_view.handler404)

    # Testing the returned status code on each view function
    def test_home_handler404_view_returned_status_code(self):
        response = self.client.get(reverse('home:404'))
        self.assertEqual(response.status_code, 404)

    # Testing wich template is loaded on each view function
    def test_home_handler404_view_template_load(self):
        response = self.client.get(reverse('home:404'))
        self.assertTemplateUsed(response, 'home/pages/404.html')
