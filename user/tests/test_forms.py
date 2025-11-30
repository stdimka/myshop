import pytest
from django.contrib.auth.models import User
from django.core import mail
from django.test import RequestFactory

from user.forms import LoginForm, RegistrationForm, MyPasswordResetForm, MySetPasswordForm


@pytest.mark.django_db
class TestForms:

    def test_registration_form_unique_email(self):
        User.objects.create_user(username="existing", email="a@a.com", password="pass123")
        form = RegistrationForm(data={
            "username": "newuser",
            "email": "a@a.com",
            "password1": "complexpass123",
            "password2": "complexpass123",
        })
        assert not form.is_valid()
        assert "email" in form.errors

    def test_registration_form_unique_username(self):
        User.objects.create_user(username="existinguser", email="b@b.com", password="pass123")
        form = RegistrationForm(data={
            "username": "existinguser",
            "email": "new@example.com",
            "password1": "complexpass123",
            "password2": "complexpass123",
        })
        assert not form.is_valid()
        assert "username" in form.errors

    def test_registration_form_widgets(self):
        form = RegistrationForm()

        assert form.fields["username"].widget.attrs.get("class") == "Input"
        assert form.fields["username"].widget.attrs.get("placeholder") == "Никнейм"

        assert form.fields["email"].widget.attrs.get("class") == "Input"
        assert form.fields["email"].widget.attrs.get("placeholder") == "E-mail"

        assert form.fields["password1"].widget.attrs.get("class") == "Input"
        assert form.fields["password1"].widget.attrs.get("placeholder") == "Пароль"

        assert form.fields["password2"].widget.attrs.get("class") == "Input"
        assert form.fields["password2"].widget.attrs.get("placeholder") == "Повторите пароль"

    def test_login_form_widgets(self):
        form = LoginForm()

        assert form.fields["username"].widget.attrs.get("class") == "Input"
        assert form.fields["username"].widget.attrs.get("placeholder") == "Логин"

        assert form.fields["password"].widget.attrs.get("class") == "Input"
        assert form.fields["password"].widget.attrs.get("placeholder") == "Пароль"



@pytest.mark.django_db
class TestPasswordForms:

    @pytest.fixture(autouse=True)
    def setup_factory(self):
        self.factory = RequestFactory()

    def test_password_reset_form_existing_email(self, user):
        request = self.factory.post('/password_reset/')
        form = MyPasswordResetForm(data={"email": user.email})
        assert form.is_valid()
        form.save(
            request=request,
            from_email="noreply@example.com",
        )
        assert len(mail.outbox) == 1
        assert user.email in mail.outbox[0].to

    def test_password_reset_form_nonexistent_email(self, user):
        request = self.factory.post('/password_reset/')
        form = MyPasswordResetForm(data={"email": "wrong@example.com"})
        assert form.is_valid()
        form.save(
            request=request,
            from_email="noreply@example.com",
        )
        assert len(mail.outbox) == 0

    def test_set_password_form_valid(self, user):
        form = MySetPasswordForm(
            user=user,
            data={"new_password1": "NewStrongPass123", "new_password2": "NewStrongPass123"}
        )
        assert form.is_valid()
        form.save()
        user.refresh_from_db()
        assert user.check_password("NewStrongPass123")

    def test_set_password_form_mismatch(self, user):
        form = MySetPasswordForm(
            user=user,
            data={"new_password1": "pass1", "new_password2": "pass2"}
        )
        assert not form.is_valid()
        assert "new_password2" in form.errors