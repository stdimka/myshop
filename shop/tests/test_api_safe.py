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
def test_api_order_list(admin_client):
    url = reverse("shop_order")
    response = admin_client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_api_order_list_contains_user(admin_client, db):
    user = User.objects.create_user(username="list_user_api")
    order = Order.objects.create(user=user, status="pending")
    url = reverse("shop_order")
    response = admin_client.get(url)
    assert response.status_code == 200
    assert str(order.id) in response.content.decode()
