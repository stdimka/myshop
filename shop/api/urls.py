from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserRegisterAPIView, UserProfileAPIView

from .views import (
    ProductViewSet,
    ProductReviewViewSet,
    CategoryViewSet,
    OrderViewSet,
    CartViewSet,
)

router = DefaultRouter()
router.register(r"products", ProductViewSet, basename="api-products")
router.register(r"categories", CategoryViewSet, basename="api-categories")
router.register(r"orders", OrderViewSet, basename="orders")
router.register(r"cart", CartViewSet, basename="cart")

urlpatterns = [
    path("users/register/", UserRegisterAPIView.as_view(), name="api-user-register"),
    path("users/me/", UserProfileAPIView.as_view(), name="api-user-me"),
    path("", include(router.urls)),

    path(
        "products/<int:product_id>/reviews/",
        ProductReviewViewSet.as_view({
            "get": "list",
            "post": "create",
        }),
        name="api-product-reviews",
    ),
]
