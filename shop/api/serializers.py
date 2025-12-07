from rest_framework import serializers
from shop.models import Product, Review, OrderItem, Order
from shop.models import Category


class ProductListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = (
            "id",
            "name",
            "slug",
            "price",
            "image",
            "is_active",
            "stock",
        )


class ProductDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = (
            "id",
            "name",
            "slug",
            "description",
            "price",
            "image",
            "is_active",
            "stock",
            "created_at",
        )


class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Review
        fields = ("id", "user", "rating", "comment", "created_at")

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'slug', 'price', 'image', 'is_active', 'stock']


class CategorySerializer(serializers.ModelSerializer):
    products_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Category
        fields = ["id", "name", "slug", "products_count"]



class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.name", read_only=True)
    product_price = serializers.DecimalField(
        source="product.price", max_digits=10, decimal_places=2, read_only=True
    )

    class Meta:
        model = OrderItem
        fields = ["id", "product", "product_name", "product_price", "quantity", "price"]


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(source="orderitem_set", many=True, read_only=True)
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    status = serializers.CharField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Order
        fields = ["id", "user", "status", "total_price", "items", "created_at"]
        read_only_fields = ["user", "status", "total_price", "items", "created_at"]



class CartItemSerializer(serializers.Serializer):
    """
    Сериализатор для одного товара в корзине
    """
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1)

    product_name = serializers.CharField(read_only=True)
    product_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    stock = serializers.IntegerField(read_only=True)
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    def validate_product_id(self, value):
        try:
            product = Product.objects.get(pk=value, is_active=True)
        except Product.DoesNotExist:
            raise serializers.ValidationError("Товар не найден или недоступен")
        self.context['product'] = product  # сохраняем для use в create/update
        return value

    def validate_quantity(self, value):
        product = self.context.get('product')
        if product and value > product.stock:
            raise serializers.ValidationError(f"Максимальное количество доступно: {product.stock}")
        return value

    def to_representation(self, instance):
        """
        Преобразуем в красивый JSON для ответа
        """
        product = Product.objects.get(pk=instance['product_id'])
        return {
            "product_id": product.id,
            "product_name": product.name,
            "product_price": product.price,
            "quantity": instance['quantity'],
            "stock": product.stock,
            "total_price": round(product.price * instance['quantity'], 2)
        }

