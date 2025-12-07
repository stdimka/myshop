from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    ProductViewSet,
    ProductReviewViewSet,
    CategoryViewSet,
    OrderViewSet,
    CartViewSet,  # ✅ Импорт есть
)

router = DefaultRouter()
router.register(r"products", ProductViewSet, basename="api-products")
router.register(r"categories", CategoryViewSet, basename="api-categories")
router.register(r"orders", OrderViewSet, basename="orders")
router.register(r"cart", CartViewSet, basename="cart")  # ✅ Регистрируем CartViewSet

urlpatterns = [
    # ✅ Включаем все стандартные роуты DRF
    path("", include(router.urls)),

    # ✅ Отзывы к продукту
    path(
        "products/<int:product_id>/reviews/",
        ProductReviewViewSet.as_view({
            "get": "list",
            "post": "create",
        }),
        name="api-product-reviews",
    ),
]
