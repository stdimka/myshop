from django.db import models, transaction
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.text import slugify
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from datetime import timedelta
import uuid


class Category(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


# ------------------------------
# Product
# ------------------------------
class Product(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    unit = models.CharField(max_length=50, default="шт")
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="products"
    )
    image = models.ImageField(upload_to="products/", blank=True, null=True)
    specs = models.JSONField(default=dict, blank=True)
    is_active = models.BooleanField(default=True)
    stock = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name) or str(uuid.uuid4())[:8]
            slug = base_slug
            counter = 1
            while Product.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def is_in_stock(self):
        """Проверка, есть ли товар на складе."""
        return self.stock > 0

    def __str__(self):
        return self.name


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
    order_id = models.CharField(max_length=255, unique=True, null=True, blank=True)  # 👈 теперь допускает null
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="cart")
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        creating = self._state.adding

        # 👇 Генерируем order_id только для pending / paid
        if self.status != "cart" and not self.order_id:
            date_part = timezone.now().strftime("%Y%m%d")
            self.order_id = f"{date_part}__{self.user.id}__{uuid.uuid4().hex[:6]}"

        super().save(*args, **kwargs)


    def add_product(self, product, quantity=1):
        """Добавляет продукт в заказ или корзину."""
        item, created = OrderItem.objects.get_or_create(
            order=self,
            product=product,
            defaults={"price": product.price, "quantity": quantity},
        )
        if not created:
            item.quantity += quantity
            item.save(update_fields=["quantity"])
        self.recalculate_total()

    def recalculate_total(self):
        """Перерасчёт суммы заказа."""
        total = sum(item.price * item.quantity for item in self.items.all())
        self.total_price = total
        self.save(update_fields=["total_price", "updated_at"])

    def to_pending(self):
        if self.status != "cart":
            return
        self.status = "pending"
        self.save()
        from .models import Payment
        Payment.process_auto(self.user)

    @classmethod
    def cleanup_expired_carts(cls):
        """Удаляет все корзины (status='cart'), старше 7 дней."""
        limit = timezone.now() - timedelta(days=7)
        cls.objects.filter(status="cart", updated_at__lt=limit).delete()

    @classmethod
    def cleanup_old_pending(cls, days=100):
        """Удаляет старые неоплаченные pending-заказы."""
        limit = timezone.now() - timedelta(days=days)
        old_orders = cls.objects.filter(status="pending", updated_at__lt=limit)

        for order in old_orders:
            # если заказ уже оплачен — не трогаем
            if hasattr(order, "payment") and order.payment.status == "completed":
                continue
            order.delete()

    def __str__(self):
        return f"Order #{self.id} ({self.status})"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # НЕ вызываем recalculate_total здесь

    def __str__(self):
        return f"{self.product.name} x{self.quantity}"



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
        """Проводит оплату заказа, если достаточно средств."""
        if order.status != "pending":
            return None

        profile = order.user.userprofile
        if profile.balance < order.total_price:
            return None

        # Проверка: если уже есть завершённый платёж
        existing_payment = getattr(order, "payment", None)
        if existing_payment and existing_payment.status == "completed":
            return existing_payment

        # Списываем средства
        profile.balance -= order.total_price
        profile.save(update_fields=["balance"])

        payment, _ = cls.objects.get_or_create(order=order)
        payment.status = "completed"
        payment.save(update_fields=["status"])

        # Меняем статус заказа на "paid"
        order.status = "paid"
        order.save(update_fields=["status", "updated_at"])

        return payment

    @classmethod
    @transaction.atomic
    def process_auto(cls, user):
        """Автоматическая оплата всех pending-заказов при наличии средств."""
        profile = user.userprofile
        pending_orders = Order.objects.filter(user=user, status="pending").order_by("created_at")

        for order in pending_orders:
            profile.refresh_from_db()
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

    def __str__(self):
        return f"{self.user.username}: {self.rating}/5"


# ------------------------------
# Signals
# ------------------------------


@receiver(post_save, sender=Payment)
def check_auto_payment(sender, instance, created, **kwargs):
    """Автоматическая проверка автооплаты при создании Payment."""
    if created and instance.status == "completed":
        instance.order.status = "paid"
        instance.order.save(update_fields=["status"])
