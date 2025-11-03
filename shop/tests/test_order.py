import pytest
from datetime import timedelta
from django.utils import timezone
from freezegun import freeze_time

from shop.models import Order, OrderItem


@pytest.mark.django_db
class TestOrder:

    def test_total_price_recalculates_on_item_change(self, user, product_factory):
        """Автоматический пересчет total_price при изменении корзины."""
        product1 = product_factory(price=50)
        product2 = product_factory(price=30)

        order = Order.objects.create(user=user, status="cart")
        OrderItem.objects.create(order=order, product=product1, quantity=2, price=product1.price)
        OrderItem.objects.create(order=order, product=product2, quantity=1, price=product2.price)

        order.recalculate_total()
        assert order.total_price == 2*50 + 30

    def test_order_id_generated_on_pending(self, user, product_factory):
        """При переходе корзины в заказ генерируется order_id."""
        order = Order.objects.create(user=user, status="cart")
        product = product_factory()
        OrderItem.objects.create(order=order, product=product, quantity=1, price=product.price)

        order.to_pending()  # метод перевода корзины в pending и генерации order_id
        assert order.status == "pending"
        assert "__" in order.order_id
        assert str(user.id) in order.order_id

    def test_old_pending_orders_deleted(self, user, make_order):
        """Проверка удаления старых заказов в статусе pending."""
        # Симулируем старый заказ
        # old_order.created_at = timezone.now() - timedelta(days=120)
        # old_order.save()

        # Создаём второй заказ «10 дней назад»
        many_days_ago = timezone.now() - timedelta(days=120)
        with freeze_time(many_days_ago):
            old_order = make_order(user=user, status="pending")

        Order.cleanup_old_pending()
        assert not Order.objects.filter(id=old_order.id).exists()
