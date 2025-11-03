from decimal import Decimal

import pytest
from datetime import timedelta
from django.utils import timezone
from freezegun import freeze_time

from shop.models import Order, OrderItem, Product


@pytest.mark.django_db
class TestUserProfile:

    def test_get_balance_returns_correct_value(self, user):
        """Проверка метода get_balance."""
        profile = user.userprofile
        profile.balance = Decimal("150.75")
        profile.save()
        assert profile.get_balance() == Decimal("150.75")

    def test_cart_is_created_automatically(self, user):
        """При первом вызове get_cart создается корзина со статусом cart."""
        profile = user.userprofile
        cart = profile.get_cart()
        assert cart.status == "cart"
        assert cart.user == user

    def test_cart_auto_deleted_after_7_days(self, user):
        """Корзина старше 7 дней удаляется при следующем вызове get_cart."""
        profile = user.userprofile
        # cart = profile.get_cart()  # Убрали (user)
        # # Симулируем старую корзину
        # cart.updated_at = timezone.now() - timedelta(days=8)
        # cart.save()
        #
        many_days_ago = timezone.now() - timedelta(days=8)
        with freeze_time(many_days_ago):
            cart = profile.get_cart()

        new_cart = profile.get_cart()
        assert new_cart.id != cart.id  # старая корзина удалена, создана новая
        assert new_cart.status == "cart"

    def test_get_unpaid_orders_returns_only_pending_orders(self, user, make_order):
        """Метод get_unpaid_orders возвращает только заказы с статусом pending и правильную сумму."""
        pending_order = make_order(user=user, status="pending", total_price=50)
        _ = make_order(user=user, status="paid", total_price=30)

        result = user.userprofile.get_unpaid_orders()  # Убрали (user)
        orders = result["orders"]
        total = result["total"]

        assert pending_order in orders
        assert total == 50
        assert all(o.status == "pending" for o in orders)

    def test_get_cart_returns_existing_cart(self, user, make_order):
        """Если корзина существует и не старше 7 дней, get_cart возвращает её."""
        order = make_order(user=user, status="cart")
        profile = user.userprofile
        cart = profile.get_cart()
        assert cart.id == order.id

    def test_cart_created_if_none_exists(self, user):
        """Если корзины нет, get_cart создает новую."""
        profile = user.userprofile
        # Удаляем все корзины пользователя
        Order.objects.filter(user=user, status="cart").delete()
        cart = profile.get_cart()  # Убрали (user)
        assert cart is not None
        assert cart.status == "cart"
        assert cart.user == user
