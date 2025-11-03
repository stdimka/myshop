import pytest
from datetime import timedelta
from freezegun import freeze_time
from django.utils import timezone
from user.models import UserToken
from shop.models import Order, Payment


@pytest.mark.django_db
class TestSystemSignalsAndJobs:
    """Тестирование сигналов и фоновых задач"""

    def test_generate_order_id_on_pending_transition(self, user_with_balance, product_in_stock):
        """Проверка генерации order_id"""
        order = Order.objects.create(user=user_with_balance, status="cart")
        order.add_product(product_in_stock, quantity=2)
        order.save()

        # Переход корзины в заказ
        order.to_pending()

        assert order.status == "pending"
        assert order.order_id.startswith(timezone.now().strftime("%Y%m%d"))
        assert str(user_with_balance.id) in order.order_id

    def test_auto_payment_trigger_on_pending(self, user_with_balance, product_in_stock):
        """Проверка автооплаты при переходе в pending"""
        userprofile = user_with_balance.userprofile
        initial_balance = userprofile.balance
        print("userprofile.balance =", userprofile.balance)

        order = Order.objects.create(user=user_with_balance, status="cart")
        order.add_product(product_in_stock, quantity=2)
        print("order.total_price = ", order.total_price)
        order.to_pending()  # должно автоматически списать средства

        userprofile.refresh_from_db()
        order.refresh_from_db()
        assert order.status == "paid"
        assert userprofile.balance == initial_balance - order.total_price

    def test_auto_payment_trigger_on_balance_increase(self, user, product_in_stock):
        """Проверка автооплаты при пополнении баланса"""
        order = Order.objects.create(user=user, status="cart")
        order.add_product(product_in_stock, quantity=3)
        order.to_pending()  # недостаточно средств — заказ остаётся pending

        assert order.status == "pending"

        # Пополняем баланс
        profile = user.userprofile
        profile.balance = order.total_price
        profile.save()

        # После сигнала проверки — заказ должен быть оплачен
        order.refresh_from_db()
        assert order.status == "paid"

    def test_cart_auto_deletion(self, user):
        """Автоудаление корзины старше 7 дней"""
        # Создаём новый заказ
        fresh_order = Order.objects.create(user=user, status="cart")

        # Создаём второй заказ «10 дней назад»
        ten_days_ago = timezone.now() - timedelta(days=10)
        with freeze_time(ten_days_ago):
            old_order = Order.objects.create(user=user, status="cart")

        Order.cleanup_expired_carts()

        assert not Order.objects.filter(id=old_order.id).exists()
        assert Order.objects.filter(id=fresh_order.id).exists()

    def test_pending_order_auto_deletion(self, user):
        """Автоудаление pending-заказов старше 100 дней"""

        fresh_order = Order.objects.create(user=user, status="pending")

        # Создаём второй заказ «101 дней назад»
        many_days_ago = timezone.now() - timedelta(days=101)
        with freeze_time(many_days_ago):
            old_order = Order.objects.create(user=user, status="pending")

        Order.cleanup_old_pending()

        assert not Order.objects.filter(id=old_order.id).exists()
        assert Order.objects.filter(id=fresh_order.id).exists()

    def test_auto_delete_expired_tokens(self, user):
        """Автоматическое удаление просроченных токенов"""
        token_valid = UserToken.objects.create(
            user=user,
            token="valid_token",
            token_type="refresh",
            expires_at=timezone.now() + timedelta(days=1)
        )
        token_expired = UserToken.objects.create(
            user=user,
            token="expired_token",
            token_type="refresh",
            expires_at=timezone.now() - timedelta(days=1)
        )

        UserToken.cleanup_expired()

        assert UserToken.objects.filter(id=token_valid.id).exists()
        assert not UserToken.objects.filter(id=token_expired.id).exists()

