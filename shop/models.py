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
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def is_in_stock(self):
        """Проверка, есть ли товар на складе."""
        return self.stock > 0


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
        if self.status == "pending" and not self.order_id:
            date_part = timezone.now().strftime("%Y%m%d")
            self.order_id = f"{date_part}-{self.user.id}-{uuid.uuid4().hex[:6]}"
        super().save(*args, **kwargs)

    def add_product(self, product, quantity=1):
        item, created = OrderItem.objects.get_or_create(
            order=self, product=product, defaults={"price": product.price, "quantity": quantity}
        )
        if not created:
            item.quantity += quantity
            item.save(update_fields=["quantity"])
        self.recalculate_total()

    def recalculate_total(self):
        """
        Перерасчёт суммы заказа
        """
        total = sum(item.price * item.quantity for item in self.items.all())
        self.total_price = total
        self.save(update_fields=["total_price", "updated_at"])

    def to_pending(self):
        if self.status != "cart":
            return
        self.status = "pending"
        self.save()
        from .models import Payment
        Payment.process(self)


    @classmethod
    def cleanup_expired_carts(cls):
        limit = timezone.now() - timedelta(days=7)
        cls.objects.filter(status="cart", updated_at__lt=limit).delete()

    @classmethod
    def cleanup_old_pending(cls, days=100):
        limit = timezone.now() - timedelta(days=days)
        cls.objects.filter(status="pending", updated_at__lt=limit).delete()


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.order.recalculate_total()


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
        if order.status != "pending":
            return None
        profile = order.user.userprofile
        if profile.balance < order.total_price:
            return None

        # списываем деньги
        profile.balance -= order.total_price
        profile.save()

        payment = cls.objects.create(order=order, status="completed")
        order.status = "paid"
        order.save(update_fields=["status", "updated_at"])
        return payment

    @classmethod
    @transaction.atomic
    def process_auto(cls, user):
        profile = user.userprofile
        pending_orders = Order.objects.filter(user=user, status="pending").order_by("created_at")

        for order in pending_orders:
            if profile.balance >= order.total_price:
                cls.process(order)
                profile.refresh_from_db()
            else:
                break


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
    instance.order.recalculate_total()



@receiver(post_save, sender=Payment)
def check_auto_payment(sender, instance, created, **kwargs):
    if created and instance.status == "completed":
        instance.order.status = "paid"
        instance.order.save(update_fields=["status"])


