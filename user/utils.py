from django.core.mail import send_mail
from django.urls import reverse
from django.conf import settings
from .models import UserToken

def send_email_verification(user):
    token = UserToken.generate(user, token_type="email_verify", expires_in_minutes=60)
    verify_url = settings.SITE_URL + reverse("auth_email_verify") + f"?token={token.token}"

    send_mail(
        subject="Подтверждение email",
        message=f"Перейдите по ссылке для подтверждения: {verify_url}",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
    )
