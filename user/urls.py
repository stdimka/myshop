# user/urls.py
from django.urls import path
from . import views  # ← подразумевается, что у тебя есть views.py в user/

app_name = 'user'  # ← необязательно, но желательно для namespace

urlpatterns = [
    # Регистрация
    path('register/', views.register_view, name='register'),
    # Вход
    path('login/', views.login_view, name='login'),
    # Выход
    path('logout/', views.logout_view, name='logout'),
    # Профиль
    path('profile/', views.profile_view, name='profile'),
    # Другие URL...
]