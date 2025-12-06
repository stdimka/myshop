from user.views import views_auth, views_account
from user.views.views_account import AccountView

user_urls = [
    # Аутентификация
    ("auth_registration", views_auth.RegistrationView, "users/auth/registration.html", 200),
    ("auth_login", views_auth.LoginView, "users/auth/login.html", 200),
    ("auth_logout", views_auth.LogoutView, None, 200),
    ("auth_email_verify", views_auth.EmailVerifyView, "???", 200),
    ("auth_email_resend_verification", views_auth.ResendVerificationView, "???", 200),
    ("auth_password_reset", views_auth.PasswordResetView, "???", 200),
    ("auth_password_reset_confirm", views_auth.PasswordResetConfirmView, "???", 200),
    #("auth_password_change", views_auth.PasswordChangeView, "???", 200),

    # Управление аккаунтом
    ('account_profile', AccountView, {}, 200),
    ("account_orders", views_account.OrderHistoryView, "???", 200),
]
