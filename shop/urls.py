# shop/urls_account.py
from django.urls import path
from . import views as shop_views



urlpatterns = [
    #path("home", shop_views.HomeView.as_view(), name="home"),

    # Products
    path("products/", shop_views.ProductListView.as_view(), name="shop_products"),
    path("products_search/", shop_views.ProductSearchView.as_view(), name="shop_products_search"),
    path("product_detail/", shop_views.ProductDetailView.as_view(), name="shop_product_detail"),
    path("product_review_add/", shop_views.ProductReviewAddView.as_view(), name="shop_product_review_add"),
    path("product_reviews/", shop_views.ProductReviewListView.as_view(), name="shop_product_reviews"),

    # Orders
    path("order/", shop_views.OrderListView.as_view(), name="shop_order"),
    path("order_add/", shop_views.OrderAddView.as_view(), name="shop_order_add"),
    path("order_remove/", shop_views.OrderRemoveView.as_view(), name="shop_order_remove"),
    path("order_update/", shop_views.OrderUpdateView.as_view(), name="shop_order_update"),
    path("order_checkout/", shop_views.OrderCheckoutView.as_view(), name="shop_order_checkout"),
    path("order_detail/", shop_views.OrderDetailView.as_view(), name="shop_order_detail"),
    path("orders/", shop_views.OrderHistoryView.as_view(), name="shop_orders"),

    # Payments
    path("payment_process/", shop_views.PaymentProcessView.as_view(), name="shop_payment_process"),
    path("payment_confirm/", shop_views.PaymentConfirmView.as_view(), name="shop_payment_confirm"),
    path("payment_cancel/", shop_views.PaymentCancelView.as_view(), name="shop_payment_cancel"),

    # Reviews
    path("review_add/", shop_views.ReviewAddView.as_view(), name="shop_review_add"),
    path("review_update/", shop_views.ReviewUpdateView.as_view(), name="shop_review_update"),
    path("review_delete/", shop_views.ReviewDeleteView.as_view(), name="shop_review_delete"),


    # Главная страница магазина (например, каталог)
    #path('', views.ProductListView.as_view(), name='product_list'),
    # Страница товара
    #path('product/<slug:slug>/', views.ProductDetailView.as_view(), name='product_detail'),
    # Корзина
    #path('cart/', views.CartView.as_view(), name='cart'),
    # Оформление заказа
    #path('checkout/', views.CheckoutView.as_view(), name='checkout'),
    # Другие URL...
]