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
def test_product_detail_view(client, db):
    product = Product.objects.create(name="Safe Product", price=10)
    url = reverse("shop_product_detail", kwargs={"pk": product.id})
    response = client.get(url)
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
def test_review_creation_with_product_and_user(db):
    user = User.objects.create_user(username="reviewuser")
    product = Product.objects.create(name="Product for Review", price=5)
    review = Review.objects.create(user=user, product=product, text="Good")
    assert review.user == user
    assert review.product == product
    assert review.text == "Good"

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
def test_product_str_method(db):
    product = Product.objects.create(name="StrProduct", price=10)
    assert str(product) == "StrProduct"

@pytest.mark.django_db
def test_order_str_method(db):
    user = User.objects.create_user(username="strorderuser")
    order = Order.objects.create(user=user, status="pending")
    assert str(order) == f"Order {order.id} - pending"

@pytest.mark.django_db
def test_review_str_method(db):
    user = User.objects.create_user(username="strreviewuser")
    product = Product.objects.create(name="ReviewProduct", price=5)
    review = Review.objects.create(user=user, product=product, text="Nice")
    assert str(review) == f"Review by {user.username} on {product.name}"

@pytest.mark.django_db
def test_product_list_contains_created_product(client, db):
    Product.objects.create(name="ListProduct", price=20)
    url = reverse("shop_products")
    response = client.get(url)
    assert b"ListProduct" in response.content

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
def test_review_linked_to_product(db):
    user = User.objects.create_user(username="linkreviewuser")
    product = Product.objects.create(name="LinkedProduct", price=15)
    review = Review.objects.create(user=user, product=product, text="Nice")
    assert review.product == product

@pytest.mark.django_db
def test_review_linked_to_user(db):
    user = User.objects.create_user(username="linkuserreview")
    product = Product.objects.create(name="ProductUserLink", price=10)
    review = Review.objects.create(user=user, product=product, text="Cool")
    assert review.user == user

@pytest.mark.django_db
def test_product_list_view_contains_multiple_products(client, db):
    Product.objects.create(name="Prod1", price=1)
    Product.objects.create(name="Prod2", price=2)
    url = reverse("shop_products")
    response = client.get(url)
    assert b"Prod1" in response.content and b"Prod2" in response.content

@pytest.mark.django_db
def test_order_count_increases(db):
    initial_count = Order.objects.count()
    user = User.objects.create_user(username="countuser")
    Order.objects.create(user=user, status="pending")
    assert Order.objects.count() == initial_count + 1
