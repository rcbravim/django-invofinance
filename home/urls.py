from django.urls import path

from . import views

app_name = 'home'

urlpatterns = [
    path('', views.index, name='index'),
    path('index/', views.index),
    path('register/', views.register, name='register'),
    path('404/', views.handler404),
]
