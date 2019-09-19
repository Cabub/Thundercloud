from django.urls import path, include
from django.contrib.auth import views as auth_views
from .views import register

urlpatterns = [
    path('login/', auth_views.LoginView.as_view()),
    path('logout/', auth_views.LogoutView.as_view()),
    path('change_password/', auth_views.PasswordChangeView.as_view()),
    path('change_password/done/', auth_views.PasswordChangeDoneView.as_view()),
    path('password_reset/', auth_views.PasswordResetView.as_view()),
    path('password_reset_done/', auth_views.PasswordResetDoneView.as_view()),
    path('register/', register)
]
