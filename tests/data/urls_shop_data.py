from shop import views as shop_views

shop_urls = [
    # Home Page
    ("home", shop_views.HomeView, "???", 200),

    # Products
    ("shop_products", shop_views.ProductListView, "???", 200),
    ("shop_products_search", shop_views.ProductSearchView, "???", 200),
    ("shop_product_detail", shop_views.ProductDetailView, "{'pk': 1}", 200),
    ("shop_product_review_add", shop_views.ProductReviewAddView, "???", 200),
    ("shop_product_reviews", shop_views.ProductReviewListView, "???", 200),

    # Orders
    ("shop_order", shop_views.OrderListView, "???", 200),
    ("shop_order_add", shop_views.OrderAddView, "???", 200),
    ("shop_order_remove", shop_views.OrderRemoveView, "???", 200),
    ("shop_order_update", shop_views.OrderUpdateView, "???", 200),
    ("shop_order_checkout", shop_views.OrderCheckoutView, "???", 200),
    ("shop_order_detail", shop_views.OrderDetailView, "???", 200),
    ("shop_orders", shop_views.OrderHistoryView, "???", 200),

    # Payments
    ("shop_payment_process", shop_views.PaymentProcessView, "???", 200),
    ("shop_payment_confirm", shop_views.PaymentConfirmView, "???", 200),
    ("shop_payment_cancel", shop_views.PaymentCancelView, "???", 200),

    # Reviews
    ("shop_review_add", shop_views.ReviewAddView, "???", 200),
    ("shop_review_update", shop_views.ReviewUpdateView, "???", 200),
    ("shop_review_delete", shop_views.ReviewDeleteView, "???", 200),
]