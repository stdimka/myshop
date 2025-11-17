# shop/views_auth.py
from django.views import generic
from django.views.generic import ListView, DetailView, View
from django.shortcuts import render, get_object_or_404
from .models import Product, Category  # ← Убедись, что модель Product существует


    # Products
class HomeView(generic.TemplateView):
    template_name = 'home.html'

class ProductListView(generic.TemplateView):
    pass

class ProductSearchView(generic.TemplateView):
    pass

class ProductDetailView(generic.TemplateView):
    pass

class ProductReviewAddView(generic.TemplateView):
    pass

class ProductReviewListView(generic.TemplateView):
    pass

    # Orders
class OrderListView(generic.TemplateView):
    pass

class OrderAddView(generic.TemplateView):
    pass

class OrderRemoveView(generic.TemplateView):
    pass

class OrderUpdateView(generic.TemplateView):
    pass

class OrderCheckoutView(generic.TemplateView):
    pass

class OrderDetailView(generic.TemplateView):
    pass

class OrderHistoryView(generic.TemplateView):
    pass

    # Payments
class PaymentProcessView(generic.TemplateView):
    pass

class PaymentConfirmView(generic.TemplateView):
    pass

class PaymentCancelView(generic.TemplateView):
    pass

    # Reviews
class ReviewAddView(generic.TemplateView):
    pass

class ReviewUpdateView(generic.TemplateView):
    pass

class ReviewDeleteView(generic.TemplateView):
    pass

# Пример списка товаров
# class ProductListView(ListView):
#     model = Product
#     template_name = 'home.html'  # или 'product_list.html', если у тебя есть такой шаблон
#     context_object_name = 'products'
#     paginate_by = 20  # по ТЗ
#
# # Пример страницы товара
# class ProductDetailView(DetailView):
#     model = Product
#     template_name = 'product_detail.html'  # ← Убедись, что шаблон существует
#     context_object_name = 'product'
#     slug_field = 'slug'  # ← если в URL используешь <slug:slug>
#     slug_url_kwarg = 'slug'
#
# # Пример корзины (CBV)
# class CartView(ListView):  # или View, если не нужно отображать список
#     template_name = 'cart.html'  # ← Убедись, что шаблон существует
#     context_object_name = 'cart_items'  # ← если передаешь список
#
#     def get_queryset(self):
#         # Пример: корзина хранится в сессии
#         cart = self.request.session.get('cart', {})
#         # Тут можно преобразовать `cart` в объекты Product и их количество
#         # Пока возвращаем пустой список, чтобы не было ошибки
#         return []
#
# # Пример оформления заказа (CBV)
# class CheckoutView(View):
#     template_name = 'checkout.html'  # ← Убедись, что шаблон существует
#
#     def get(self, request, *args, **kwargs):
#         # Отображение формы оформления заказа
#         return render(request, self.template_name)
#
#     def post(self, request, *args, **kwargs):
#         # Обработка отправленной формы
#         # Здесь будет логика создания заказа и оплаты
#         return render(request, self.template_name, {'message': 'Order placed successfully!'})