import pytest
from django.urls import reverse
from shop.models import Product, Order, Review
from django.contrib.auth.models import User


@pytest.mark.django_db
def test_products_search_returns_ok(client):
    url = reverse("shop_products_search")
    response = client.get(url, {"q": "test"})
    assert response.status_code == 200


@pytest.mark.django_db
def test_order_list_view_access(admin_client):
    url = reverse("shop_order")
    response = admin_client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_create_user_in_db(db):
    user = User.objects.create_user(username="safeuser", email="safe@example.com", password="123")
    assert user.id is not None
    assert user.username == "safeuser"


@pytest.mark.django_db
def test_order_creation_with_user(db):
    user = User.objects.create_user(username="orderuser")
    order = Order.objects.create(user=user, status="pending")
    assert order.user == user
    assert order.status == "pending"


@pytest.mark.django_db
def test_multiple_products_in_db(db):
    p1 = Product.objects.create(name="P1", price=1)
    p2 = Product.objects.create(name="P2", price=2)
    products = Product.objects.all()
    assert len(products) >= 2


@pytest.mark.django_db
def test_order_id_auto_generated(db):
    user = User.objects.create_user(username="iduser")
    order = Order.objects.create(user=user, status="pending")
    assert order.id is not None


@pytest.mark.django_db
def test_product_price_positive(db):
    product = Product.objects.create(name="PriceTest", price=99)
    assert product.price > 0


@pytest.mark.django_db
def test_product_filter_by_price(db):
    Product.objects.create(name="Cheap", price=5)
    Product.objects.create(name="Expensive", price=100)
    expensive = Product.objects.filter(price__gte=50)
    assert len(expensive) == 1
    assert expensive.first().name == "Expensive"


@pytest.mark.django_db
def test_order_status_change(db):
    user = User.objects.create_user(username="statususer")
    order = Order.objects.create(user=user, status="pending")
    order.status = "paid"
    order.save()
    assert order.status == "paid"


@pytest.mark.django_db
def test_order_has_no_items_initially(db):
    user = User.objects.create_user(username="emptyorderuser")
    order = Order.objects.create(user=user, status="pending")
    assert order.items.count() == 0


@pytest.mark.django_db
def test_order_count_increases(db):
    initial_count = Order.objects.count()
    user = User.objects.create_user(username="countuser")
    Order.objects.create(user=user, status="pending")
    assert Order.objects.count() == initial_count + 1
