# shop/urls.py
from django.urls import path
from . import views  # ← подразумевается, что у тебя есть views.py в shop/

app_name = 'shop'  # ← необязательно, но желательно для namespace

urlpatterns = [
    # Главная страница магазина (например, каталог)
    path('', views.ProductListView.as_view(), name='product_list'),
    # Страница товара
    path('product/<slug:slug>/', views.ProductDetailView.as_view(), name='product_detail'),
    # Корзина
    path('cart/', views.CartView.as_view(), name='cart'),
    # Оформление заказа
    path('checkout/', views.CheckoutView.as_view(), name='checkout'),
    # Другие URL...
]