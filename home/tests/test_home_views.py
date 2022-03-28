from django.test import TestCase
from django.urls import resolve, reverse
from home import views


class TestHomeViews(TestCase):
    # Testing the returned function on each view function
    def test_home_index_view_function(self):
        view = resolve(reverse('home:index'))
        self.assertIs(view.func, views.index)

    def test_home_index_nd_view_function(self):
        view = resolve('/index/')
        self.assertIs(view.func, views.index)

    def test_home_handler404_view_function(self):
        view = resolve('/404/')
        self.assertIs(view.func, views.handler404)

    def test_home_register_view_function(self):
        view = resolve(reverse('home:register'))
        self.assertIs(view.func, views.register)

    # Testing the returned status code on each view function
    def test_home_index_view_returned_status_code(self):
        response = self.client.get(reverse('home:index'))
        self.assertEqual(response.status_code, 200)

    def test_home_index_nd_view_returned_status_code(self):
        response = self.client.get('/index/')
        self.assertEqual(response.status_code, 200)

    def test_home_handler404_view_returned_status_code(self):
        response = self.client.get('/404/')
        self.assertEqual(response.status_code, 404)

    def test_home_register_view_returned_status_code(self):
        response = self.client.get(reverse('home:register'))
        self.assertEqual(response.status_code, 200)

    # Testing wich template is loaded on each view function
    def test_home_index_view_template_load(self):
        response = self.client.get(reverse('home:index'))
        self.assertTemplateUsed(response, 'home/pages/index.html')

    def test_home_index_nd_view_template_load(self):
        response = self.client.get('/index/')
        self.assertTemplateUsed(response, 'home/pages/index.html')

    def test_home_handler404_view_template_load(self):
        response = self.client.get('/404/')
        self.assertTemplateUsed(response, 'home/pages/404.html')

    def test_home_register_view_template_load(self):
        response = self.client.get(reverse('home:register'))
        self.assertTemplateUsed(response, 'home/pages/register.html')
