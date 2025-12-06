from django.urls import path
from user.views import views_account
from django.urls import path
from user.views.views_account import AccountView

urlpatterns = [
    path("profile/", AccountView.as_view(), name="account_profile"),
    path("orders/", views_account.OrderHistoryView.as_view(), name="account_orders"),

]



# my old version
# user/urls_account.py
# from django.urls import path
# from user import views  # ← подразумевается, что у тебя есть views_auth.py в user/

# app_name = 'user'  # ← необязательно, но желательно для namespace

# urlpatterns = [
    # Регистрация
#     path('register/', views.register_view, name='register'),
    # Вход
#     path('login/', views.login_view, name='login'),
    # Выход
#     path('logout/', views.logout_view, name='logout'),
    # Профиль
#     path('profile/', views.profile_view, name='profile'),
    # Другие URL...
# ]