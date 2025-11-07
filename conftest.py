import pytest
from decimal import Decimal

from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from shop.models import Product, Order, OrderItem, Review, Payment, Category
from user.models import UserToken, UserProfile


# ------------------------------
# USERS
# ------------------------------

@pytest.fixture
def user(db):
    """Создает обычного пользователя с профилем и нулевым балансом."""
    user = User.objects.create_user(username="testuser", password="pass123")
    # UserProfile создается автоматически через сигнал post_save
    # Если сигнал не работает — создаём принудительно:
    from user.models import UserProfile
    profile, _ = UserProfile.objects.get_or_create(user=user)
    profile.balance = Decimal("0.0")
    profile.save()
    return user


@pytest.fixture
def user_with_balance(user):
    """Пользователь с ненулевым балансом (на основе фикстуры user)."""
    profile = user.userprofile
    profile.balance = Decimal('300.00')
    profile.save()
    return user


@pytest.fixture
def token_factory(db):
    """Фабрика токенов разных типов для пользователя."""
    def create_token(user, token_type="refresh", expires_in_minutes=60):
        expires_at = timezone.now() + timedelta(minutes=expires_in_minutes)
        token = UserToken.objects.create(
            user=user,
            token_type=token_type,
            token="token_" + token_type,
            expires_at=expires_at
        )
        return token
    return create_token


# ------------------------------
# SHOP
# ------------------------------
@pytest.fixture(autouse=True)
def create_default_category(db):
    """Создаёт категорию 'General' один раз для всех тестов."""
    from shop.models import Category
    Category.objects.get_or_create(
        slug="general",
        defaults={"name": "General"}
    )


@pytest.fixture
def product_factory(db):
    from shop.models import Category
    def create_product(**kwargs):
        # Получаем или создаём категорию
        category = Category.objects.get(slug="general")
        defaults = {
            "name": "Test Product",
            "description": "Описание продукта",
            "price": Decimal("100.0"),
            "unit": "шт",
            "category": category,  # ← обязательно!
            "image": "",
            "specs": {"color": "red", "weight": "1kg"},
            "is_active": True,
            "stock": 10,
        }
        defaults.update(kwargs)
        return Product.objects.create(**defaults)
    return create_product


@pytest.fixture
def product(product_factory):
    """Обычный продукт по умолчанию."""
    return product_factory()


@pytest.fixture
def product_in_stock():
    from shop.models import Category
    category = Category.objects.get(slug="general")
    return Product.objects.create(
        name="Тестовый товар",
        price=Decimal("100.0"),
        stock=10,
        unit="шт",
        specs={"color": "red"},
        category=category  # ← добавлено
    )


@pytest.fixture
def make_order(db, product_factory):
    """Фабрика заказов с позициями."""
    def create_order(user, status="cart", items_count=1, item_price=None):
        order = Order.objects.create(user=user, status=status)
        for _ in range(items_count):
            price = Decimal(item_price) if item_price is not None else Decimal("100.00")
            product = product_factory(price=price)
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=1,
                price=price
            )
        order.recalculate_total()
        return order
    return create_order


@pytest.fixture
def pending_order(make_order, user):
    """Заказ со статусом pending (но без оплаты)."""
    return make_order(user=user, status="pending")


@pytest.fixture
def paid_order(make_order, user_with_balance):
    """Оплаченный заказ."""
    order = make_order(user=user_with_balance, status="cart")  # сначала корзина
    order.to_pending()  # → pending → оплата → paid
    order.refresh_from_db()
    return order


@pytest.fixture
def review_factory(db):
    """Фабрика отзывов."""
    def create_review(user, product, **kwargs):
        defaults = {"rating": 5, "comment": "Отличный товар!"}
        defaults.update(kwargs)
        return Review.objects.create(user=user, product=product, **defaults)
    return create_review


@pytest.fixture
def review(review_factory, user, product):
    """Простой отзыв."""
    return review_factory(user=user, product=product)