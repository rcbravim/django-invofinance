from django.urls import path

from home.views import (error_view, index_view, logout_view, register_view,
                        server_error_view)

app_name = 'home'

urlpatterns = [
    # INDEX
    path('index/', index_view.IndexView.as_view()),
    path('', index_view.IndexView.as_view(), name='index'),
    path('index/auth/', index_view.IndexView.as_view(), name='index_auth'),

    # LOGOUT
    path('logout/', logout_view.LogoutView.as_view(), name='logout'),

    # REGISTER
    path('register/', register_view.RegisterView.as_view(), name='register'),
    path('register/new/', register_view.RegisterView.as_view(), name='register_new'),  # noqa: E501
    path('register/verify/', register_view.RegisterView.as_view(), name='register_verify'),  # noqa: E501

    # FAILED
    path('register/failed/', register_view.RegisterView.as_view(), name='register_failed'),  # noqa: E501

    # 404
    path('404/', error_view.handler404, name='404'),

    # 500
    path('500/', server_error_view.handler500, name='500'),
]

#handler404 = 'home.views.handler404' # noqa: E265
