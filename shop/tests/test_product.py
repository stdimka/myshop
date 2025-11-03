import pytest
from shop.models import Product


@pytest.mark.django_db
class TestProduct:

    def test_product_creation(self, product):
        """Проверка создания продукта по умолчанию."""
        assert product.id is not None
        assert product.name == "Test Product"
        assert product.is_active
        assert product.stock > 0
        assert isinstance(product.specs, dict)

    def test_product_search_by_name(self, product_factory):
        """Поиск продукта по имени."""
        product1 = product_factory(name="Red Chair")
        product2 = product_factory(name="Blue Table")
        results = Product.objects.filter(name__icontains="Chair")
        assert product1 in results
        assert product2 not in results

    # TODO подумать, надо ли это
    def test_product_filter_by_stock(self, product_factory):
        """Проверка наличия продукта на складе."""
        available = product_factory(stock=5)
        sold_out = product_factory(stock=0)
        assert available.is_in_stock() is True
        assert sold_out.is_in_stock() is False

    def test_edit_product_specs(self, product):
        """Редактирование характеристик JSON."""
        product.specs["color"] = "blue"
        product.save()
        updated_product = Product.objects.get(id=product.id)
        assert updated_product.specs["color"] == "blue"
