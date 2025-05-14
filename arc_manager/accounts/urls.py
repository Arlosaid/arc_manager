from django.urls import path, reverse_lazy
from django.contrib.auth import views as auth_views

from accounts.views import SecurePasswordResetView
from .forms import CustomAuthenticationForm

app_name = 'accounts'

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(
            template_name='auth/login.html',
            authentication_form=CustomAuthenticationForm
        ), name='login'),
    path('logout/', auth_views.LogoutView.as_view(
            http_method_names=['get', 'post'],
            next_page='accounts:login'
        ), name='logout'),
    path('password_reset/', SecurePasswordResetView.as_view(
        template_name='auth/password_reset.html',
        email_template_name='auth/password_reset_email.html',
        subject_template_name='auth/password_reset_subject.txt',
        success_url=reverse_lazy('accounts:password_reset_done')
    ), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(
            template_name='auth/password_reset_done.html'
        ), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
            template_name='auth/password_reset_confirm.html',
            success_url=reverse_lazy('accounts:password_reset_complete')
        ), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(
            template_name='auth/password_reset_complete.html'
        ), name='password_reset_complete'),
]