from django.urls import path, include
from django.contrib.auth import views as auth_views
from .views import (
    register, reset_password, reset_password_done, change_password
)


urlpatterns = [
    path('login/', auth_views.LoginView.as_view()),
    path('logout/', auth_views.LogoutView.as_view()),
    path('change_password/', change_password),
    path(
        'change_password/done/',
        auth_views.PasswordChangeDoneView.as_view(),
        name='password_change_done'
    ),
    path('password_reset/', reset_password, name='password_reset'),
    path(
        'password_reset/done/', reset_password_done, name='password_reset_done'
    ),
    path('register/', register)
]
