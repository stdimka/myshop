from rest_framework import viewsets, permissions, filters, status
from django.db.models import Avg
from django_filters.rest_framework import DjangoFilterBackend
from shop.models import Category, Order, Cart, OrderItem, Product, Review
from .serializers import CategorySerializer, OrderSerializer
from django.shortcuts import get_object_or_404

from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from .serializers import (
    ProductListSerializer,
    ProductDetailSerializer,
    ReviewSerializer,
)
from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import get_user_model

from .serializers import UserRegisterSerializer, UserProfileSerializer


class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    """
    /api/products/
    /api/products/{id}/
    """

    queryset = Product.objects.filter(is_active=True)
    serializer_class = ProductListSerializer

    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]

    # ✅ Поиск
    search_fields = ["name", "description"]

    # ✅ Фильтр по цене
    filterset_fields = {
        "price": ["gte", "lte"],  # min_price, max_price
    }

    # ✅ Сортировка
    ordering_fields = ["price", "created_at"]
    ordering = ["-created_at"]

    def get_serializer_class(self):
        if self.action == "retrieve":
            return ProductDetailSerializer
        return ProductListSerializer


class ProductReviewViewSet(viewsets.ModelViewSet):
    """
    /api/products/{product_id}/reviews/
    """

    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        return Review.objects.filter(product_id=self.kwargs["product_id"])

    def perform_create(self, serializer):
        serializer.save(
            user=self.request.user,
            product_id=self.kwargs["product_id"]
        )


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.annotate(
        products_count=Avg("products__id")
    )
    serializer_class = CategorySerializer


class OrderViewSet(viewsets.ModelViewSet):
    """
    /api/orders/
    /api/orders/{id}/
    """

    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Пользователь видит только свои заказы
        return Order.objects.filter(user=self.request.user).order_by("-created_at")

    def create(self, request, *args, **kwargs):
        """
        Создание заказа на основе корзины пользователя.
        """
        user = request.user
        cart = request.session.get("cart", {})  # корзина в сессии, если используем session-based
        if not cart:
            return Response({"detail": "Корзина пуста."}, status=status.HTTP_400_BAD_REQUEST)

        order_items = []
        total_price = 0

        for product_id_str, quantity in cart.items():
            product_id = int(product_id_str)
            product = get_object_or_404(Product, id=product_id, is_active=True)

            if product.stock < quantity:
                return Response(
                    {"detail": f"Недостаточно товара '{product.name}' на складе."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Рассчёт цены
            item_price = product.price * quantity
            total_price += item_price

            order_items.append({
                "product": product,
                "quantity": quantity,
                "price": product.price,
            })

        # Создание заказа
        order = Order.objects.create(
            user=user,
            total_price=total_price,
            status="pending",  # начальный статус
        )

        # Создание OrderItem
        for item in order_items:
            OrderItem.objects.create(
                order=order,
                product=item["product"],
                quantity=item["quantity"],
                price=item["price"],
            )
            # Уменьшаем остаток на складе
            item["product"].stock -= item["quantity"]
            item["product"].save()

        # Очистка корзины
        request.session["cart"] = {}
        request.session.modified = True

        serializer = self.get_serializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class CartViewSet(viewsets.ViewSet):
    """
    Управление корзиной через сессию или JWT-пользователя.
    Эндпоинт: /api/cart/
    """

    permission_classes = [IsAuthenticatedOrReadOnly]

    def _get_cart(self):
        # Получаем корзину из сессии или создаём пустую
        cart = self.request.session.get("cart", {})
        return cart

    def _save_cart(self, cart):
        self.request.session["cart"] = cart
        self.request.session.modified = True

    def list(self, request):
        """GET /api/cart/ - показать содержимое корзины"""
        cart = self._get_cart()
        items = []
        total_price = 0
        for product_id_str, quantity in cart.items():
            try:
                product = Product.objects.get(pk=int(product_id_str))
            except Product.DoesNotExist:
                continue
            item_total = product.price * quantity
            total_price += item_total
            items.append({
                "id": product.id,
                "name": product.name,
                "price": product.price,
                "quantity": quantity,
                "total": item_total,
            })
        return Response({"items": items, "total_price": total_price})

    def create(self, request):
        """POST /api/cart/ - добавить товар в корзину"""
        product_id = request.data.get("product_id")
        quantity = int(request.data.get("quantity", 1))
        try:
            product = Product.objects.get(pk=product_id)
        except Product.DoesNotExist:
            return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)

        cart = self._get_cart()
        cart[str(product_id)] = cart.get(str(product_id), 0) + quantity
        self._save_cart(cart)
        return Response({"message": "Product added to cart"}, status=status.HTTP_201_CREATED)

    def partial_update(self, request, pk=None):
        """PATCH /api/cart/{product_id}/ - изменить количество"""
        quantity = int(request.data.get("quantity", 1))
        cart = self._get_cart()
        if pk is None or str(pk) not in cart:
            return Response({"error": "Product not in cart"}, status=status.HTTP_404_NOT_FOUND)
        if quantity <= 0:
            cart.pop(str(pk))
        else:
            cart[str(pk)] = quantity
        self._save_cart(cart)
        return Response({"message": "Cart updated"})

    def destroy(self, request, pk=None):
        """DELETE /api/cart/{product_id}/ - удалить товар"""
        cart = self._get_cart()
        if pk and str(pk) in cart:
            cart.pop(str(pk))
            self._save_cart(cart)
            return Response({"message": "Product removed"})
        return Response({"error": "Product not in cart"}, status=status.HTTP_404_NOT_FOUND)


User = get_user_model()


class UserRegisterAPIView(generics.CreateAPIView):
    """
    POST /api/users/register/
    {
        "username": "test",
        "email": "test@mail.com",
        "password": "123456"
    }
    """
    queryset = User.objects.all()
    serializer_class = UserRegisterSerializer
    permission_classes = [AllowAny]


class UserProfileAPIView(generics.RetrieveUpdateAPIView):
    """
    GET  /api/users/me/
    PATCH /api/users/me/
    """
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user
