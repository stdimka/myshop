
from django.contrib import admin
from django.urls import path, include
from django.conf import settings  # ← Обязательно
from django.conf.urls.static import static  # ← Обязательно

urlpatterns = [
    path('admin/', admin.site.urls),
    # ... твои URL ...
]

# Только для разработки (когда DEBUG=True)
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    # Также, если есть MEDIA файлы:
    # urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
