from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, include, reverse_lazy
from account import views

app_name = "account"

urlpatterns = [
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),
    path('user_admin/', views.user_admin, name='user_admin'),
    path('password_reset/', auth_views.PasswordResetView.as_view(
        template_name='account/password_reset.html',
        email_template_name='account/password_reset_email.html',
        subject_template_name='account/password_reset_subject.txt',
        success_url=reverse_lazy('account:password_reset_done')),
        name='password_reset'),
    path('password_reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='account/password_reset_confirm.html',
        success_url=reverse_lazy('account:password_reset_complete')),
        name='password_reset_confirm'),
    path('password_reset_done/', auth_views.PasswordResetDoneView.as_view(
        template_name='account/password_reset_done.html'),
        name='password_reset_done'),
    path('password_reset_complete/', auth_views.PasswordResetCompleteView.as_view(
        template_name='account/password_reset_complete.html'),
        name='password_reset_complete'),
]
