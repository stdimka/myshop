import pytest
from django.urls import reverse
from shop.models import Product, Order, Review
from django.contrib.auth.models import User

@pytest.mark.django_db
def test_api_get_products(client, db):
    url = reverse("shop_products")
    response = client.get(url)
    assert response.status_code == 200

@pytest.mark.django_db
def test_api_get_product_detail(client, db):
    product = Product.objects.create(name="API Product", price=10)
    url = reverse("shop_product_detail", kwargs={"pk": product.id})
    response = client.get(url)
    assert response.status_code == 200
    assert b"API Product" in response.content

@pytest.mark.django_db
def test_api_order_list(admin_client):
    url = reverse("shop_order")
    response = admin_client.get(url)
    assert response.status_code == 200

@pytest.mark.django_db
def test_api_create_product(admin_client, db):
    url = reverse("shop_products")
    data = {"name": "New API Product", "price": 25}
    response = admin_client.post(url, data)
    assert response.status_code in (200, 201)
    assert Product.objects.filter(name="New API Product").exists()

@pytest.mark.django_db
def test_api_create_order(admin_client, db):
    user = User.objects.create_user(username="api_order_user")
    url = reverse("shop_order_add")
    data = {"user": user.id, "status": "pending"}
    response = admin_client.post(url, data)
    assert response.status_code in (200, 201)
    assert Order.objects.filter(user=user).exists()

@pytest.mark.django_db
def test_api_get_order_detail(admin_client, db):
    user = User.objects.create_user(username="api_order_detail_user")
    order = Order.objects.create(user=user, status="pending")
    url = reverse("shop_order_detail", kwargs={"pk": order.id})
    response = admin_client.get(url)
    assert response.status_code == 200

@pytest.mark.django_db
def test_api_create_review(admin_client, db):
    user = User.objects.create_user(username="api_review_user")
    product = Product.objects.create(name="Review API Product", price=10)
    url = reverse("shop_review_add")
    data = {"user": user.id, "product": product.id, "text": "Nice"}
    response = admin_client.post(url, data)
    assert response.status_code in (200, 201)
    assert Review.objects.filter(product=product, user=user).exists()

@pytest.mark.django_db
def test_api_get_review_list(client, db):
    url = reverse("shop_product_reviews", kwargs={"pk": 1})
    response = client.get(url)
    assert response.status_code == 200

@pytest.mark.django_db
def test_api_filter_products_by_price(client, db):
    Product.objects.create(name="Cheap", price=5)
    Product.objects.create(name="Expensive", price=50)
    url = reverse("shop_products")
    response = client.get(url, {"min_price": 10})
    assert response.status_code == 200
    content = response.content.decode()
    assert "Expensive" in content

@pytest.mark.django_db
def test_api_search_products(client, db):
    Product.objects.create(name="Searchable Product", price=20)
    url = reverse("shop_products_search")
    response = client.get(url, {"q": "Searchable"})
    assert response.status_code == 200
    assert b"Searchable Product" in response.content

@pytest.mark.django_db
def test_api_order_count(admin_client, db):
    initial_count = Order.objects.count()
    url = reverse("shop_order_add")
    user = User.objects.create_user(username="count_api_user")
    data = {"user": user.id, "status": "pending"}
    admin_client.post(url, data)
    assert Order.objects.count() == initial_count + 1

@pytest.mark.django_db
def test_api_product_update(admin_client, db):
    product = Product.objects.create(name="Old Name", price=15)
    url = reverse("shop_product_detail", kwargs={"pk": product.id})
    data = {"name": "Updated Name", "price": 15}
    response = admin_client.post(url, data)
    assert response.status_code in (200, 201)
    product.refresh_from_db()
    assert product.name == "Updated Name"

@pytest.mark.django_db
def test_api_order_update_status(admin_client, db):
    user = User.objects.create_user(username="update_order_user")
    order = Order.objects.create(user=user, status="pending")
    url = reverse("shop_order_update", kwargs={"pk": order.id})
    data = {"status": "paid"}
    response = admin_client.post(url, data)
    assert response.status_code in (200, 201)
    order.refresh_from_db()
    assert order.status == "paid"

@pytest.mark.django_db
def test_api_review_update(admin_client, db):
    user = User.objects.create_user(username="update_review_user")
    product = Product.objects.create(name="Review Update Product", price=10)
    review = Review.objects.create(user=user, product=product, text="Old Text")
    url = reverse("shop_review_update", kwargs={"pk": review.id})
    data = {"text": "New Text"}
    response = admin_client.post(url, data)
    assert response.status_code in (200, 201)
    review.refresh_from_db()
    assert review.text == "New Text"

@pytest.mark.django_db
def test_api_product_detail_404(client):
    url = reverse("shop_product_detail", kwargs={"pk": 9999})
    response = client.get(url)
    assert response.status_code == 404

@pytest.mark.django_db
def test_api_order_detail_404(admin_client):
    url = reverse("shop_order_detail", kwargs={"pk": 9999})
    response = admin_client.get(url)
    assert response.status_code == 404

@pytest.mark.django_db
def test_api_review_detail_404(admin_client):
    url = reverse("shop_review_update", kwargs={"pk": 9999})
    response = admin_client.get(url)
    assert response.status_code == 404

@pytest.mark.django_db
def test_api_product_list_contains_multiple_products(client, db):
    Product.objects.create(name="Prod1", price=1)
    Product.objects.create(name="Prod2", price=2)
    url = reverse("shop_products")
    response = client.get(url)
    content = response.content.decode()
    assert "Prod1" in content and "Prod2" in content

@pytest.mark.django_db
def test_api_order_list_contains_user(admin_client, db):
    user = User.objects.create_user(username="list_user_api")
    order = Order.objects.create(user=user, status="pending")
    url = reverse("shop_order")
    response = admin_client.get(url)
    assert response.status_code == 200
    assert str(order.id) in response.content.decode()
