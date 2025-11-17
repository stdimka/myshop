from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
import uuid


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="userprofile")
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)

    CART_EXPIRATION_DAYS = 7

    def get_balance(self):
        """Возвращает текущий баланс пользователя."""
        return self.balance

    def get_cart(self):
        """Возвращает актуальную корзину или создаёт новую."""
        from shop.models import Order
        now = timezone.now()
        expiration_time = now - timedelta(days=self.CART_EXPIRATION_DAYS)

        # удаляем устаревшие корзины
        Order.objects.filter(user=self.user, status="cart", updated_at__lt=expiration_time).delete()

        # ищем актуальную
        cart = Order.objects.filter(user=self.user, status="cart").order_by("-updated_at").first()
        if cart:
            return cart

        # создаём новую
        return Order.objects.create(user=self.user, status="cart")

    def get_unpaid_orders(self):
        """Возвращает все заказы pending и общую сумму."""
        from shop.models import Order
        pending_orders = Order.objects.filter(user=self.user, status="pending")
        total = sum(order.total_price for order in pending_orders)
        return {"orders": list(pending_orders), "total": total}

    def __str__(self):
        return f"Profile of {self.user.username}"


# ------------------------------
# UserToken
# ------------------------------
class UserToken(models.Model):
    TOKEN_TYPES = (
        ("refresh", "Refresh"),
        ("email_verify", "Email Verification"),
        ("password_reset", "Password Reset"),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="tokens")
    token = models.CharField(max_length=255, unique=True)
    token_type = models.CharField(max_length=20, choices=TOKEN_TYPES)
    expires_at = models.DateTimeField()
    revoked = models.BooleanField(default=False)

    def is_valid(self):
        """Проверка валидности токена."""
        return not self.revoked and self.expires_at > timezone.now()

    def revoke(self):
        """Отозвать токен."""
        self.revoked = True
        self.save(update_fields=["revoked"])

    @classmethod
    def cleanup_expired(cls):
        """Удаление всех истекших токенов."""
        cls.objects.filter(expires_at__lt=timezone.now()).delete()

    @classmethod
    def generate(cls, user, token_type="refresh", expires_in_minutes=60):
        """Создает новый токен."""
        token_value = uuid.uuid4().hex
        expires = timezone.now() + timedelta(minutes=expires_in_minutes)
        return cls.objects.create(
            user=user,
            token=token_value,
            token_type=token_type,
            expires_at=expires
        )

    def __str__(self):
        return f"{self.user.username} - {self.token_type}"


# ------------------------------
# Signals
# ------------------------------
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver


@receiver(pre_save, sender=UserProfile)
def detect_balance_increase(sender, instance, **kwargs):
    if not instance.pk:
        return  # новый профиль — пропускаем

    try:
        old = UserProfile.objects.get(pk=instance.pk)
    except UserProfile.DoesNotExist:
        return

    instance._balance_increased = instance.balance > old.balance


@receiver(post_save, sender=UserProfile)
def auto_process_pending_orders(sender, instance, **kwargs):
    if getattr(instance, "_balance_increased", False):
        from shop.models import Payment
        Payment.process_auto(instance.user)

