# shop/views.py
from django.views.generic import ListView, DetailView, View
from django.shortcuts import render, get_object_or_404
from .models import Product, Category  # ← Убедись, что модель Product существует

# Пример списка товаров
class ProductListView(ListView):
    model = Product
    template_name = 'home.html'  # или 'product_list.html', если у тебя есть такой шаблон
    context_object_name = 'products'
    paginate_by = 20  # по ТЗ

# Пример страницы товара
class ProductDetailView(DetailView):
    model = Product
    template_name = 'product_detail.html'  # ← Убедись, что шаблон существует
    context_object_name = 'product'
    slug_field = 'slug'  # ← если в URL используешь <slug:slug>
    slug_url_kwarg = 'slug'

# Пример корзины (CBV)
class CartView(ListView):  # или View, если не нужно отображать список
    template_name = 'cart.html'  # ← Убедись, что шаблон существует
    context_object_name = 'cart_items'  # ← если передаешь список

    def get_queryset(self):
        # Пример: корзина хранится в сессии
        cart = self.request.session.get('cart', {})
        # Тут можно преобразовать `cart` в объекты Product и их количество
        # Пока возвращаем пустой список, чтобы не было ошибки
        return []

# Пример оформления заказа (CBV)
class CheckoutView(View):
    template_name = 'checkout.html'  # ← Убедись, что шаблон существует

    def get(self, request, *args, **kwargs):
        # Отображение формы оформления заказа
        return render(request, self.template_name)

    def post(self, request, *args, **kwargs):
        # Обработка отправленной формы
        # Здесь будет логика создания заказа и оплаты
        return render(request, self.template_name, {'message': 'Order placed successfully!'})