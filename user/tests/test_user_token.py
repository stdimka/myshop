import pytest
from django.utils import timezone
from datetime import timedelta
from user.models import UserToken


@pytest.mark.django_db
class TestUserToken:

    def test_generate_and_validate_email_token(self, user, token_factory):
        """Создание токена email_verify и проверка его валидности."""
        token = token_factory(user, token_type="email_verify")
        assert token.is_valid()
        assert token.token_type == "email_verify"
        assert token.user == user

    def test_expired_token_becomes_invalid(self, user):
        """Токен, срок действия которого истек, считается недействительным."""
        token = UserToken.objects.create(
            user=user,
            token_type="password_reset",
            token="expired_token",
            expires_at=timezone.now() - timedelta(minutes=1)
        )
        assert not token.is_valid()

    def test_revoke_token(self, user, token_factory):
        """Отозванный токен становится недействительным."""
        token = token_factory(user, token_type="refresh")
        token.revoke()
        token.refresh_from_db()
        assert token.revoked
        assert not token.is_valid()

    def test_cleanup_expired_tokens(self, user):
        """Удаление всех просроченных токенов."""
        expired_token = UserToken.objects.create(
            user=user,
            token_type="email_verify",
            token="expired",
            expires_at=timezone.now() - timedelta(days=1)
        )
        # Метод очистки должен удалить expired токен
        UserToken.cleanup_expired()
        assert not UserToken.objects.filter(id=expired_token.id).exists()

    def test_multiple_token_types(self, user, token_factory):
        """Проверка работы разных типов токенов для одного пользователя."""
        refresh_token = token_factory(user, token_type="refresh")
        email_token = token_factory(user, token_type="email_verify")
        password_token = token_factory(user, token_type="password_reset")

        assert refresh_token.is_valid()
        assert email_token.is_valid()
        assert password_token.is_valid()
        assert refresh_token.token_type == "refresh"
        assert email_token.token_type == "email_verify"
        assert password_token.token_type == "password_reset"
