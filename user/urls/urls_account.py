from django.urls import path
from user.views import views_account
from django.urls import path
from user.views.views_account import AccountView

urlpatterns = [
    path("profile/", AccountView.as_view(), name="account_profile"),
    path("orders/", views_account.OrderHistoryView.as_view(), name="account_orders"),

]
