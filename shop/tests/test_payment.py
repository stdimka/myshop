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
        """При оплате заказа меняются статусы и заказа, и оплаты."""
        order = make_order(user=user_with_balance, status="pending", total_price=Decimal("100"))
        payment = Payment.process(order)  # метод должен менять статус на paid и создавать инвойс

        order.refresh_from_db()
        assert order.status == "paid"
        assert payment.status == "completed"

    def test_balance_decreased_after_payment(self, user_with_balance, make_order):
        """Баланс пользователя уменьшается на сумму оплаченного заказа."""
        initial_balance = user_with_balance.userprofile.balance
        order = make_order(user=user_with_balance, status="pending", total_price=100)
        Payment.process(order)
        user_with_balance.userprofile.refresh_from_db()
        assert user_with_balance.userprofile.balance == initial_balance - 100

    def test_auto_payment_of_multiple_pending_orders(self, user_with_balance, make_order):
        """Если баланс достаточно, оплачиваются несколько заказов одновременно."""
        user_profile = user_with_balance.userprofile
        user_profile.balance = 300
        user_profile.save()

        # создаем несколько заказов
        order1 = make_order(user=user_with_balance, status="pending", total_price=100)
        order2 = make_order(user=user_with_balance, status="pending", total_price=150)
        order3 = make_order(user=user_with_balance, status="pending", total_price=100)

        # создаем платёж, который проверяет все неоплаченные заказы
        Payment.process_auto(user_with_balance)

        # проверка статусов и остатка баланса
        order1.refresh_from_db()
        order2.refresh_from_db()
        order3.refresh_from_db()
        user_profile.refresh_from_db()

        assert order1.status == "paid"
        assert order2.status == "paid"
        assert order3.status == "pending"  # недостаточно средств для третьего
        assert user_profile.balance == 50  # 300 - (100+150)

