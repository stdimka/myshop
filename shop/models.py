from django.db import models, transaction
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.text import slugify
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from datetime import timedelta
import uuid

from user.models import UserProfile


# безопасное получение профиля пользователя
def _get_profile(user):
    from user.models import UserProfile
    profile, _ = UserProfile.objects.get_or_create(user=user)
    return profile



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
        related_name="products",
        null=True,
        blank=True,
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
    # допускаем NULL для cart (чтобы несколько корзин не конфликтовали)
    order_id = models.CharField(max_length=255, unique=True, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="cart")
    total_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        creating = self._state.adding

        # генерируем order_id только если статус не cart и order_id ещё нет
        if self.status != "cart" and not self.order_id:
            date_part = timezone.now().strftime("%Y%m%d")
            self.order_id = f"{date_part}__{self.user.id}__{uuid.uuid4().hex[:6]}"

        super().save(*args, **kwargs)

        # НО: автооплата запускается при переводе в pending (в to_pending)
        # и при явном пополнении баланса (user.models сигнал).
        # Здесь автозапуска не ставим, чтобы избежать двойных вызовов.

    def add_product(self, product, quantity=1):
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
        total = sum(item.price * item.quantity for item in self.items.all())
        self.total_price = total
        # сохраняем минимально нужные поля
        self.save(update_fields=["total_price", "updated_at"])

    def to_pending(self):
        if self.status != "cart":
            return
        self.status = "pending"
        self.save()
        # ✅ гарантируем профиль перед автоплатежом
        from user.models import UserProfile
        UserProfile.objects.get_or_create(user=self.user)
        from .models import Payment
        Payment.process_auto(self.user)

    @classmethod
    def cleanup_expired_carts(cls):
        limit = timezone.now() - timedelta(days=7)
        cls.objects.filter(status="cart", updated_at__lt=limit).delete()

    @classmethod
    def cleanup_old_pending(cls, days=100):
        """Удаляет старые pending-заказы, только если они действительно неоплачены."""
        limit = timezone.now() - timedelta(days=days)
        old_orders = cls.objects.filter(status="pending", updated_at__lt=limit)
        for order in old_orders:
            # если есть связанный платёж и он completed — пропускаем
            if hasattr(order, "payment") and order.payment.status == "completed":
                continue
            order.delete()

    def __str__(self):
        return f"Order #{self.id} ({self.status})"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=12, decimal_places=2)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # ВАЖНО: пересчитываем total при изменении позиции
        try:
            self.order.recalculate_total()
        except Exception:
            # безопасно игнорируем, если что-то не доступно (например при удалении test-DB state)
            pass

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
        if order.status != "pending":
            return None

        profile = _get_profile(order.user)  # ✅ безопасно

        if profile.balance < order.total_price:
            return None

        existing_payment = getattr(order, "payment", None)
        if existing_payment and existing_payment.status == "completed":
            return existing_payment

        profile.balance -= order.total_price
        profile.save(update_fields=["balance"])

        payment, _ = cls.objects.get_or_create(order=order)
        payment.status = "completed"
        payment.save(update_fields=["status"])

        order.status = "paid"
        order.save(update_fields=["status", "updated_at"])

        return payment

    @classmethod
    @transaction.atomic
    def process_auto(cls, user):
        pending_orders = Order.objects.filter(user=user, status="pending").order_by("created_at")
        for order in pending_orders:
            # ✅ каждый раз берём актуальный профиль (создастся, если нужно)
            profile = _get_profile(user)
            if profile.balance >= order.total_price:
                cls.process(order)
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


class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"Cart {self.user}"


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name="items", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def get_total_price(self):
        return self.quantity * self.product.price


# ------------------------------
# Signals — пересчёт total при изменениях OrderItem
# ------------------------------
@receiver(post_save, sender=OrderItem)
@receiver(post_delete, sender=OrderItem)
def update_order_total(sender, instance, **kwargs):
    # гарантируем, что при любом изменении позиции сумма заказа актуальна
    try:
        instance.order.recalculate_total()
    except Exception:
        pass


@receiver(post_save, sender=Payment)
def ensure_order_paid(sender, instance, created, **kwargs):
    """
    Сигнал: если платёж окончательный — убедимся, что заказ помечен как paid.
    (дублирующая страховка, не должна вызывать двойного списания).
    """
    if instance.status == "completed":
        if instance.order.status != "paid":
            instance.order.status = "paid"
            instance.order.save(update_fields=["status"])

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Signal: создать профиль при создании пользователя."""
    if created:
        UserProfile.objects.create(user=instance)
