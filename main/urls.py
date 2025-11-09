
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView  # ← Добавь это
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    # Главная страница — каталог товаров
    path('', TemplateView.as_view(template_name='home.html'), name='home'),  # ← или include('shop.urls')
    # Подключаем URL'ы приложений
    path('shop/', include('shop.urls')),  # ← или используй shop.urls для корня
    path('user/', include('user.urls')),  # ← регистрация, профиль и т.д.
    # Если будешь делать API
    # path('api/', include('api.urls')),
]


if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
    # Если есть MEDIA:
    # urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


