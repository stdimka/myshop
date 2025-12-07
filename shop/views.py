from django.views import generic
from django.views.generic import ListView, DetailView, TemplateView
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy
from django.core.paginator import Paginator

from .models import Product, Order, OrderItem, Review
from django.db.models import Q
from .models import Product, Category
from django.shortcuts import render


# -------------------------
# ГЛАВНАЯ И КАТАЛОГ
# -------------------------

class HomeView(ListView):
    model = Product
    template_name = 'home.html'
    context_object_name = 'products'

    def get_queryset(self):
        qs = Product.objects.all()
        q = self.request.GET.get('q')
        category_id = self.request.GET.get('category')
        min_price = self.request.GET.get('min_price')
        max_price = self.request.GET.get('max_price')

        if q:
            qs = qs.filter(name__icontains=q)
        if category_id:
            qs = qs.filter(category_id=category_id)
        if min_price:
            qs = qs.filter(price__gte=min_price)
        if max_price:
            qs = qs.filter(price__lte=max_price)

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q', '')
        context['categories'] = Category.objects.all()
        context['selected_category'] = self.request.GET.get('category', '')
        context['min_price'] = self.request.GET.get('min_price', '')
        context['max_price'] = self.request.GET.get('max_price', '')
        return context




class ProductListView(ListView):
    model = Product
    template_name = 'home.html'
    context_object_name = 'object_list'



class ProductSearchView(ListView):
    model = Product
    template_name = 'home.html'
    context_object_name = 'products'
    paginate_by = 12  # Количество товаров на странице

    def get_queryset(self):
        qs = Product.objects.filter(is_active=True)
        q = self.request.GET.get("q")
        min_price = self.request.GET.get("min_price")
        max_price = self.request.GET.get("max_price")
        sort = self.request.GET.get("sort")

        if q:
            qs = qs.filter(Q(name__icontains=q) | Q(description__icontains=q))

        if min_price:
            qs = qs.filter(price__gte=min_price)
        if max_price:
            qs = qs.filter(price__lte=max_price)

        if sort == "price_asc":
            qs = qs.order_by("price")
        elif sort == "price_desc":
            qs = qs.order_by("-price")
        elif sort == "new":
            qs = qs.order_by("-created_at")
        # по умолчанию — без сортировки

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Сохраняем параметры поиска и фильтры для формы
        context["query"] = self.request.GET.get("q", "")
        context["min_price"] = self.request.GET.get("min_price", "")
        context["max_price"] = self.request.GET.get("max_price", "")
        context["sort"] = self.request.GET.get("sort", "new")
        return context



class ProductDetailView(DetailView):
    model = Product
    template_name = "product_detail.html"
    slug_field = "slug"
    slug_url_kwarg = "slug"


# -------------------------
# ОТЗЫВЫ
# -------------------------

class ProductReviewAddView(TemplateView):
    template_name = "review/add-update-delete-review.html"


class ProductReviewListView(TemplateView):
    template_name = "review/add-update-delete-review.html"


class ReviewAddView(TemplateView):
    template_name = "review/add-update-delete-review.html"


class ReviewUpdateView(TemplateView):
    template_name = "review/add-update-delete-review.html"


class ReviewDeleteView(TemplateView):
    template_name = "review/add-update-delete-review.html"


# -------------------------
# КОРЗИНА (РЕАЛЬНАЯ)
# -------------------------

class OrderListView(TemplateView):
    template_name = "shop/cart.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        cart = self.request.session.get("cart", {})
        products = Product.objects.filter(id__in=cart.keys())

        cart_items = []
        total = 0

        for product in products:
            qty = cart[str(product.id)]
            item_total = product.price * qty
            total += item_total

            cart_items.append({
                "product": product,
                "quantity": qty,
                "total": item_total
            })

        context["cart_items"] = cart_items
        context["total"] = total
        return context


class OrderAddView(generic.View):
    def post(self, request):
        product_id = request.POST.get("product_id")
        cart = request.session.get("cart", {})

        if product_id:
            cart[product_id] = cart.get(product_id, 0) + 1

        request.session["cart"] = cart
        return redirect("shop_order")


class OrderRemoveView(generic.View):
    def post(self, request):
        product_id = request.POST.get("product_id")
        cart = request.session.get("cart", {})

        if product_id in cart:
            del cart[product_id]

        request.session["cart"] = cart
        return redirect("shop_order")


class OrderUpdateView(generic.View):
    def post(self, request):
        product_id = request.POST.get("product_id")
        quantity = int(request.POST.get("quantity", 1))

        cart = request.session.get("cart", {})
        if quantity > 0:
            cart[product_id] = quantity
        else:
            cart.pop(product_id, None)

        request.session["cart"] = cart
        return redirect("shop_order")


class OrderCheckoutView(TemplateView):
    template_name = "shop/checkout.html"


class OrderDetailView(TemplateView):
    template_name = "shop/checkout.html"


class OrderHistoryView(ListView):
    template_name = "shop/order_history.html"  # лучше отдельный шаблон
    context_object_name = "orders"

    def get_queryset(self):
        user = self.request.user
        return Order.objects.filter(user=user).order_by('-created_at')

# -------------------------
# ОПЛАТА
# -------------------------

class PaymentProcessView(TemplateView):
    template_name = "shop/checkout.html"


class PaymentConfirmView(TemplateView):
    template_name = "shop/checkout.html"


class PaymentCancelView(TemplateView):
    template_name = "shop/checkout.html"



class GuidesRecipesView(TemplateView):
    template_name = "guides-recipes.html"


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