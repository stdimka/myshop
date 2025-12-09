# shop/tests/test_safe_generated.py
import pytest
from decimal import Decimal
from django.utils import timezone
from datetime import timedelta

from shop.models import (
    Product,
    Order,
    OrderItem,
    Payment,
    Review,
    Category,
    Cart,
    CartItem,
)
from user.models import UserToken


@pytest.mark.django_db
def test_product_factory_creates_product(product_factory):
    p = product_factory(name="PF Product", price=Decimal("12.50"), stock=5)
    assert p.pk is not None
    assert p.name == "PF Product"
    assert p.price == Decimal("12.50")


@pytest.mark.django_db
def test_product_slug_generated(product):
    # fixture product created via product_factory has slug generated on save
    assert product.slug and isinstance(product.slug, str)
    assert "-" not in product.slug or product.slug.isascii()


@pytest.mark.django_db
def test_product_is_in_stock(product):
    # default fixture product has stock > 0
    assert product.is_in_stock() is True
    assert product.stock > 0


@pytest.mark.django_db
def test_order_add_product_and_recalculate(make_order, user):
    # create empty order and add a product manually, then recalc
    order = Order.objects.create(user=user, status="cart")
    p = Product.objects.create(
        name="Recalc Product", slug="recalc-product", price=Decimal("7.00"), stock=10
    )
    order.add_product(p, quantity=3)
    order.refresh_from_db()
    assert order.total_price == Decimal("21.00")
    assert order.items.count() == 1


@pytest.mark.django_db
def test_pending_order_to_paid_with_balance(make_order, user_with_balance):
    # make an order with total <= user_with_balance.profile.balance
    order = make_order(user_with_balance, status="cart", items_count=1, item_price="100.00")
    # ensure profile balance is enough (fixture user_with_balance sets 300)
    assert user_with_balance.userprofile.get_balance() >= order.total_price
    # transition to pending which triggers auto-payment
    order.to_pending()
    order.refresh_from_db()
    assert order.status == "paid"
    # payment record exists
    assert hasattr(order, "payment")
    assert order.payment.status == "completed"


@pytest.mark.django_db
def test_payment_process_returns_none_when_insufficient_balance(make_order, user):
    # user fixture has balance 0
    order = make_order(user, status="pending", items_count=1, item_price="2000.00")
    # try to process payment directly
    res = Payment.process(order)
    assert res is None
    order.refresh_from_db()
    assert order.status == "pending"


@pytest.mark.django_db
def test_order_cleanup_expired_carts(make_order, user):
    # create cart and set updated_at to older than 8 days
    old_cart = make_order(user, status="cart")
    old_time = timezone.now() - timedelta(days=8)
    Order.objects.filter(pk=old_cart.pk).update(updated_at=old_time)
    # cleanup
    Order.cleanup_expired_carts()
    assert not Order.objects.filter(pk=old_cart.pk).exists()


@pytest.mark.django_db
def test_order_cleanup_old_pending_keeps_paid(make_order, user_with_balance):
    # create pending order older than threshold and mark payment completed -> should not be deleted
    order = make_order(user_with_balance, status="pending", item_price="1.00")
    # make it old
    old_time = timezone.now() - timedelta(days=200)
    Order.objects.filter(pk=order.pk).update(updated_at=old_time)
    # ensure payment completed for this order
    payment = Payment.process(order)  # should complete as user_with_balance has enough
    assert payment is not None and payment.status == "completed"
    # run cleanup
    Order.cleanup_old_pending(days=100)
    assert Order.objects.filter(pk=order.pk).exists()


@pytest.mark.django_db
def test_order_id_generated_on_status_change(user):
    order = Order.objects.create(user=user, status="cart")
    assert order.order_id is None
    order.status = "pending"
    order.save()
    assert order.order_id is not None
    assert "__" in order.order_id


@pytest.mark.django_db
def test_orderitem_str_and_total_update(make_order, user):
    order = make_order(user, status="cart", items_count=1, item_price="12.00")
    item = order.items.first()
    assert str(item).startswith(item.product.name)
    # change quantity and save -> recalc will run in OrderItem.save
    item.quantity = 3
    item.save()
    order.refresh_from_db()
    assert order.total_price == item.price * item.quantity


@pytest.mark.django_db
def test_review_creation_and_str(review, user, product):
    # review fixture created using review_factory
    assert review.pk is not None
    assert review.user == user
    assert review.product == product
    assert str(review).startswith(user.username)


@pytest.mark.django_db
def test_userprofile_get_cart_creates_cart(user):
    profile = user.userprofile
    # remove any existing carts
    Order.objects.filter(user=user, status="cart").delete()
    cart = profile.get_cart()
    assert cart is not None
    assert cart.status == "cart"


@pytest.mark.django_db
def test_userprofile_get_unpaid_orders(make_order, user):
    # create two pending orders
    o1 = make_order(user, status="pending", item_price="5.00")
    o2 = make_order(user, status="pending", item_price="7.00")
    res = user.userprofile.get_unpaid_orders()
    assert "orders" in res and "total" in res
    # total should equal sum of totals
    expected = sum(o.total_price for o in res["orders"])
    assert Decimal(res["total"]) == expected


@pytest.mark.django_db
def test_usertoken_is_valid_and_revoke(user, token_factory):
    token = token_factory(user, token_type="refresh", expires_in_minutes=10)
    assert token.is_valid() is True
    token.revoke()
    token.refresh_from_db()
    assert token.is_valid() is False


@pytest.mark.django_db
def test_usertoken_cleanup_expired(token_factory, user):
    # create expired token
    t = token_factory(user, token_type="refresh", expires_in_minutes=-10)
    # cleanup should remove it
    UserToken.cleanup_expired()
    assert not UserToken.objects.filter(pk=t.pk).exists()


@pytest.mark.django_db
def test_cart_model_and_cartitem_get_total_price(product, db, user):
    # create Cart model (note: project also keeps orders-as-cart; Cart model exists in models)
    cart = Cart.objects.create(user=user)
    ci = CartItem.objects.create(cart=cart, product=product, quantity=4)
    assert ci.get_total_price() == product.price * 4



@pytest.mark.django_db
def test_signal_creates_user_profile_on_user_create(db):
    from django.contrib.auth.models import User
    new = User.objects.create_user(username="signaluser", password="123")
    assert hasattr(new, "userprofile")
    assert new.userprofile.get_balance() == Decimal("0.0")


@pytest.mark.django_db
def test_default_category_exists():
    cat = Category.objects.filter(slug="general").first()
    assert cat is not None
    assert cat.name.lower() == "general"
