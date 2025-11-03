from django.db import models
from django.db import transaction
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.text import slugify
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from datetime import timedelta
import uuid


# ------------------------------
# Product
# ------------------------------
class Product(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    unit = models.CharField(max_length=50, default="шт")
    category_id = models.IntegerField(default=1)
    image = models.ImageField(upload_to="products/", blank=True, null=True)
    specs = models.JSONField(default=dict, blank=True)
    is_active = models.BooleanField(default=True)
    stock = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        pass

    def is_in_stock(self):
        """
        Есть ли остаток?
        В нашем случае логичнее было бы назвать is_enable
        """


# ------------------------------
# Order / OrderItem
# ------------------------------
class Order(models.Model):
    STATUS_CHOICES = (
        ("cart", "Cart"),
        ("pending", "Pending"),
        ("paid", "Paid"),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders")
    order_id = models.CharField(max_length=255, blank=True, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="cart")
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        pass

    def add_product(self, product, quantity=1):
        """
        Добавляет продукт в заказ или корзину.
        Если товар уже есть в корзине, увеличивает количество.
        """

    def recalculate_total(self):
        """
        Перерасчёт суммы заказа
        """
        total = sum(item.price * item.quantity for item in self.items.all())
        self.total_price = total
        self.save(update_fields=["total_price", "updated_at"])

    def to_pending(self):
        """
        Перевод корзины в заказ и генерация order_id.
        """

    @classmethod
    def cleanup_expired_carts(cls):
        """
        Удаляет все корзины (status='cart'), которые не изменялись более 7 дней.
        """

    @classmethod
    def cleanup_old_pending(cls, days=100):
        """
        Удаляет заказы, не оплаченные в течение 100 дней.
        """


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def save(self, *args, **kwargs):
        pass


# ------------------------------
# Payment
# ------------------------------
class Payment(models.Model):
    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("completed", "Completed"),
        ("failed", "Failed"),
        ("cancelled", "Cancelled"),
    )

    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name="payment")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)

    @classmethod
    @transaction.atomic
    def process(cls, order):
        """Оплата заказа (только для pending)."""

    @classmethod
    @transaction.atomic
    def process_auto(cls, user):
        """Автоматическая оплата всех pending-заказов при наличии средств."""


# ------------------------------
# Review
# ------------------------------
class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="reviews")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reviews")
    rating = models.PositiveSmallIntegerField(default=5)
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


# ------------------------------
# Сигналы
# ------------------------------


@receiver(post_save, sender=OrderItem)
@receiver(post_delete, sender=OrderItem)
def update_order_total(sender, instance, **kwargs):
    """
    Автоматический пересчёт total_price при изменении OrderItem
    """


@receiver(post_save, sender=Payment)
def check_auto_payment(sender, instance, created, **kwargs):
    """
    Автоматическая проверка автооплаты при создании Payment
    """

