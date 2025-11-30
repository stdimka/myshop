from django import forms
from django.contrib.auth.forms import (
    UserCreationForm, AuthenticationForm, PasswordResetForm, SetPasswordForm
)
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.urls import reverse
from user.models import UserToken
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes

class LoginForm(AuthenticationForm):
    error_messages = {
        "invalid_login": "Пожалуйста, введите правильное имя пользователя",
        "inactive": "Этот аккаунт отключён.",
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Добавляем CSS-классы и placeholder только в виджеты
        self.fields['username'].widget.attrs.update({
            'class': 'Input',
            'placeholder': 'Логин'
        })
        self.fields['password'].widget.attrs.update({
            'class': 'Input',
            'placeholder': 'Пароль'
        })


class RegistrationForm(UserCreationForm):
    error_messages = {
        "password_mismatch": "Введённые пароли не совпадают.",
    }
    email = forms.EmailField(
        required=True,
        label="E-mail",
        widget=forms.EmailInput(attrs={
            "class": "Input",
            "placeholder": "E-mail"
        })
    )

    username = forms.CharField(
        widget=forms.TextInput(attrs={
            "class": "Input",
            "placeholder": "Никнейм"
        })
    )

    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            "class": "Input",
            "placeholder": "Пароль"
        })
    )

    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            "class": "Input",
            "placeholder": "Повторите пароль"
        })
    )

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def clean_email(self):
        email = self.cleaned_data["email"].lower()
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Пользователь с таким email уже существует.")
        return email

    def clean_username(self):
        username = self.cleaned_data["username"]
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Пользователь с таким username уже существует.")
        return username



class MyPasswordResetForm(PasswordResetForm):
    error_messages = {
        "email": "Пользователь с таким email не найден.",
        "inactive": "Этот аккаунт отключён.",
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].widget.attrs.update({
            'class': 'Input',
            'placeholder': 'Введите ваш email'
        })

    def save(self, **kwargs):
        email = self.cleaned_data.get("email")
        # Получаем пользователей
        users = list(self.get_users(email))
        request = kwargs.get("request")
        use_https = kwargs.get("use_https", False)
        protocol = "https" if use_https else "http"
        domain = request.get_host() if request else "example.com"

        for user in users:
            token_obj = UserToken.generate(user, token_type="password_reset", expires_in_minutes=60)
            uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
            reset_url = f"{protocol}://{domain}{reverse('auth_password_reset_confirm', kwargs={'uidb64': uidb64, 'token': token_obj.token})}"
            try:
                send_mail(
                    subject="Сброс пароля",
                    message=f"Ссылка для сброса пароля: {reset_url}",
                    from_email=kwargs.get("from_email"),  # None → DEFAULT_FROM_EMAIL
                    recipient_list=[user.email],
                    fail_silently=False,
                )
            except Exception as e:
                print(f"[ERROR] Failed to send email to {user.email}: {e}")


class MySetPasswordForm(SetPasswordForm):
    """
    Просто кастомная форма с CSS-классами
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['new_password1'].widget.attrs.update({
            'class': 'Input',
            'placeholder': 'Новый пароль'
        })
        self.fields['new_password2'].widget.attrs.update({
            'class': 'Input',
            'placeholder': 'Повторите пароль'
        })
