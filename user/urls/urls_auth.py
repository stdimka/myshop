from django.urls import path
from user.views import views_auth

urlpatterns = [
    path('registration/', views_auth.RegistrationView.as_view(), name='auth_registration'),
    path('login/', views_auth.LoginView.as_view(), name='auth_login'),
    path('logout/', views_auth.LogoutView.as_view(), name='auth_logout'),
    path('email_verify/', views_auth.EmailVerifyView.as_view(), name='auth_email_verify'),
    path('email_resend_verification/', views_auth.ResendVerificationView.as_view(), name='auth_email_resend_verification'),
    path('password_reset/', views_auth.PasswordResetView.as_view(), name='auth_password_reset'),
    path('password_reset_confirm/<uidb64>/<token>/', views_auth.PasswordResetConfirmView.as_view(), name='auth_password_reset_confirm'),
]