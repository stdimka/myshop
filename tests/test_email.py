import pytest
from django.core import mail
from django.core.mail import send_mail

from main.settings import *
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"


@pytest.mark.django_db
def test_send_email():

    # действие
    send_mail(
        subject="Тест",
        message="Проверка отправки письма.",
        from_email="no-reply@example.com",
        recipient_list=["user@example.com"],
    )

    # проверяем, что письмо попало в outbox
    assert len(mail.outbox) == 1

    email = mail.outbox[0]

    assert email.subject == "Тест"
    assert email.body == "Проверка отправки письма."
    assert email.from_email == "no-reply@example.com"
    assert email.to == ["user@example.com"]