import pytest
from django.contrib.auth.models import User
from django.contrib.messages import get_messages
from django.core import mail
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from unittest.mock import patch

from user.models import UserToken

@pytest.mark.django_db
class TestAuthViews:

    def test_login_view_get(self, client):
        url = reverse("auth_login")
        response = client.get(url)
        assert response.status_code == 200
        assert "username" in response.content.decode()

    def test_login_view_post_valid(self, client, user):
        url = reverse("auth_login")
        response = client.post(url, {"username": "testuser", "password": "pass123"})
        assert response.status_code == 302  # редирект после логина
        assert response.url == "/"

    def test_login_view_post_invalid(self, client):
        url = reverse("auth_login")
        response = client.post(url, {"username": "wrong", "password": "wrong"})
        assert response.status_code == 200
        assert "Пожалуйста, введите правильное имя пользователя" in response.content.decode()

    def test_logout_view(self, client, user):
        client.login(username="testuser", password="pass123")
        url = reverse("auth_logout")
        response = client.post(url)
        assert response.status_code == 302
        assert response.url == "/"  # next_page

@pytest.mark.django_db
class TestRegistrationViews:

    def test_registration_view_get(self, client):
        url = reverse("auth_registration")
        response = client.get(url)
        assert response.status_code == 200
        assert "username" in response.content.decode()

    def test_registration_view_post_existing_email(self, client):
        User.objects.create_user(username="u1", email="test@example.com", password="pass123")

        url = reverse("auth_registration")
        data = {
            "username": "newuser",
            "email": "test@example.com",  # тот же email
            "password1": "strongpass123",
            "password2": "strongpass123",
        }
        response = client.post(url, data)

        assert response.status_code == 200
        assert "Пользователь с таким email уже существует." in response.content.decode()

    def test_registration_view_post_existing_username(self, client):
        User.objects.create_user(username="taken", email="x@x.com", password="pass123")

        url = reverse("auth_registration")
        data = {
            "username": "taken",  # тот же username
            "email": "new@example.com",
            "password1": "strongpass123",
            "password2": "strongpass123",
        }
        response = client.post(url, data)

        assert response.status_code == 200
        assert "Пользователь с таким username уже существует." in response.content.decode()

    def test_registration_view_passwords_do_not_match(self, client):
        url = reverse("auth_registration")
        data = {
            "username": "newuser",
            "email": "new@example.com",
            "password1": "strongpass123",
            "password2": "otherpass123",  # не совпадают
        }
        response = client.post(url, data)

        assert response.status_code == 200
        assert "Введённые пароли не совпадают." in response.content.decode()

    @pytest.mark.django_db
    def test_registration_view_post_valid(self, client):
        """Проверяем успешную регистрацию: отправку email и сообщение пользователю"""

        url = reverse("auth_registration")
        data = {
            "username": "newuser",
            "email": "new@example.com",
            "password1": "strongpass123",
            "password2": "strongpass123",
        }

        with patch("user.views.views_auth.send_email_verification") as mock_send_email:
            response = client.post(url, data, follow=True)

            # Проверка сообщений
            messages = [m.message for m in get_messages(response.wsgi_request)]
            assert "Регистрация успешна! Проверьте email для подтверждения." in messages

            # Проверка вызова функции отправки email (что функция действительно вызывалась ТОЛЬКО один раз)
            mock_send_email.assert_called_once()


@pytest.mark.django_db
class TestEmailVerifyView:

    def test_email_verify_valid_token(self, client):
        user = User.objects.create_user(username="testuser", email="x@x.com", password="pass123", is_active=False)
        token = UserToken.generate(user, token_type="email_verify", expires_in_minutes=60)

        url = reverse("auth_email_verify") + f"?token={token.token}"
        response = client.get(url, follow=True)

        # Проверка редиректа на логин
        assert response.status_code == 200

        # Пользователь активирован
        user.refresh_from_db()
        assert user.is_active is True

        # Токен отозван
        token.refresh_from_db()
        assert token.revoked is True

        # Проверка сообщений
        messages = [m.message for m in get_messages(response.wsgi_request)]
        assert "Email успешно подтвержден!" in messages

    def test_email_verify_missing_token(self, client):
        url = reverse("auth_email_verify")
        response = client.get(url, follow=True)

        assert response.status_code == 200
        messages = [m.message for m in get_messages(response.wsgi_request)]
        assert "Токен подтверждения не указан." in messages

    def test_email_verify_invalid_token(self, client):
        url = reverse("auth_email_verify") + "?token=invalidtoken123"
        response = client.get(url, follow=True)

        assert response.status_code == 200
        messages = [m.message for m in get_messages(response.wsgi_request)]
        assert "Неверный токен подтверждения." in messages

    def test_email_verify_expired_token(self, client):
        user = User.objects.create_user(username="testuser2", email="y@y.com", password="pass123", is_active=False)
        token = UserToken.generate(user, token_type="email_verify", expires_in_minutes=-1)  # сразу истёкший

        url = reverse("auth_email_verify") + f"?token={token.token}"
        response = client.get(url, follow=True)

        assert response.status_code == 200
        messages = [m.message for m in get_messages(response.wsgi_request)]
        assert "Токен истёк или был отозван." in messages


@pytest.mark.django_db
class TestResendVerificationView:

    def test_resend_verification_success(self, client):
        """Email в сессии, пользователь неактивен → письмо отправлено"""
        user = User.objects.create_user(username="testuser", email="x@x.com", password="pass123", is_active=False)
        session = client.session
        session["pending_verification_email"] = user.email
        session.save()

        url = reverse("auth_email_resend_verification")

        with patch("user.views.views_auth.send_email_verification") as mock_send_email:
            response = client.get(url, follow=True)

            # Проверка редиректа
            assert response.status_code == 200
            assert response.resolver_match.view_name == "auth_login"

            # Проверка сообщения
            messages = [m.message for m in get_messages(response.wsgi_request)]
            assert "Письмо для подтверждения email отправлено повторно." in messages

            # Проверка вызова функции отправки email
            mock_send_email.assert_called_once_with(user)

            # Email удалён из сессии
            assert "pending_verification_email" not in client.session

    def test_resend_verification_email_already_active(self, client):
        """Email в сессии, пользователь уже активен → сообщение о подтверждённом email"""
        user = User.objects.create_user(username="testuser2", email="y@y.com", password="pass123", is_active=True)
        session = client.session
        session["pending_verification_email"] = user.email
        session.save()

        url = reverse("auth_email_resend_verification")
        response = client.get(url, follow=True)

        messages = [m.message for m in get_messages(response.wsgi_request)]
        assert "Email уже подтверждён." in messages

        # Email удалён из сессии
        assert "pending_verification_email" not in client.session

    def test_resend_verification_email_missing(self, client):
        """Email отсутствует в сессии → ошибка"""
        url = reverse("auth_email_resend_verification")
        response = client.get(url, follow=True)

        messages = [m.message for m in get_messages(response.wsgi_request)]
        assert "Email для повторной отправки не найден." in messages


@pytest.mark.django_db
class TestPasswordViews:

    def test_password_reset_sends_email(self, client, user):
        url = reverse("auth_password_reset")
        response = client.post(url, {"email": user.email})

        assert response.status_code in (200, 302)
        assert len(mail.outbox) == 1
        email = mail.outbox[0]
        assert user.email in email.to
        assert "password_reset_confirm" in email.body

        # Проверка корректного uidb64
        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
        assert uidb64 in email.body

    def test_password_reset_confirm_changes_password(self, client, django_user_model):
        # Создаём пользователя
        user = django_user_model.objects.create_user(
            username="test2",
            email="test2@example.com",
            password="old_password"
        )

        # Генерируем токен через UserToken
        token_obj = UserToken.generate(user, token_type="password_reset", expires_in_minutes=60)
        token = token_obj.token

        # Кодируем pk пользователя
        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))

        # Формируем URL с обязательными параметрами
        url = reverse(
            "auth_password_reset_confirm",
            kwargs={"uidb64": uidb64, "token": token}
        )

        # POST-запрос с новым паролем
        response = client.post(url, {
            "new_password1": "new_secure_password123",
            "new_password2": "new_secure_password123",
        })

        # Проверяем успешный статус
        assert response.status_code in (200, 302)

        # Обновляем пользователя из базы
        user.refresh_from_db()
        # Проверяем, что пароль изменился
        assert user.check_password("new_secure_password123")

        # Проверяем, что токен отозван
        token_obj.refresh_from_db()
        assert not token_obj.is_valid()