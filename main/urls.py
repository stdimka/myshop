
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from django.contrib import admin

from shop.views import HomeView

urlpatterns = [
    path('administrator/', admin.site.urls),
    path('admin/', include('adminapp.urls')),
    # Главная страница — каталог товаров
    path('', HomeView.as_view(), name='home'),
    # Подключаем URL'ы приложений
    path('shop/', include('shop.urls')),  # ← или используй shop.urls для корня
    #path('user/', include('user.urls')),  # ← регистрация, профиль и т.д.
    path('auth/', include('user.urls.urls_auth')),
    path('account/', include('user.urls.urls_account')),

    # Если будешь делать API
    # path('api/', include('api.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


#if settings.DEBUG:
#    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
    # Если есть MEDIA:
    # urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


