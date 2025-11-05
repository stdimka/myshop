from decimal import Decimal

import pytest
from shop.models import Payment


@pytest.mark.django_db
class TestPayment:

    def test_payment_not_allowed_for_cart(self, user, make_order):
        """Невозможно оплатить заказ в статусе 'cart'."""
        order = make_order(user=user, status="cart")
        result = Payment.process(order)
        assert result is None
        assert order.status == "cart"

    def test_changing_order_status_on_paid(self, user_with_balance, make_order):
        order = make_order(user=user_with_balance, status="pending", item_price=100)
        payment = Payment.process(order)

        order.refresh_from_db()
        assert order.status == "paid"
        assert payment.status == "completed"

    def test_balance_decreased_after_payment(self, user_with_balance, make_order):
        order = make_order(user=user_with_balance, status="cart", item_price=100)

        # Явно обновляем сумму и перечитываем из БД
        order.recalculate_total()
        order.refresh_from_db()

        # Убеждаемся, что сумма правильная
        assert order.total_price == Decimal("100")

        # Переводим в pending → оплата
        order.to_pending()

        # Обновляем данные
        user_with_balance.userprofile.refresh_from_db()
        order.refresh_from_db()

        assert user_with_balance.userprofile.balance == Decimal("200.00")
        assert order.status == "paid"

        print("Order total_price:", order.total_price)
        print("Order items:", list(order.items.values_list('price', 'quantity')))

    def test_auto_payment_of_multiple_pending_orders(self, user_with_balance, make_order):
        profile = user_with_balance.userprofile
        profile.balance = Decimal("300")
        profile.save()

        cart1 = make_order(user=user_with_balance, status="cart", item_price=100)
        cart2 = make_order(user=user_with_balance, status="cart", item_price=150)
        cart3 = make_order(user=user_with_balance, status="cart", item_price=100)

        # Явно пересчитываем и обновляем
        for cart in [cart1, cart2, cart3]:
            cart.recalculate_total()
            cart.refresh_from_db()
            assert cart.total_price > 0

        # Переводим в pending
        cart1.to_pending()
        cart2.to_pending()
        cart3.to_pending()

        # Проверяем
        for cart in [cart1, cart2, cart3]:
            cart.refresh_from_db()
        profile.refresh_from_db()

        assert cart1.status == "paid"
        assert cart2.status == "paid"
        assert cart3.status == "pending"
        assert profile.balance == Decimal("50")