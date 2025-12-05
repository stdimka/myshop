from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from django.contrib import admin

from shop.views import HomeView

urlpatterns = [
                  path('administrator/', admin.site.urls),

                  path('admin/', include('adminapp.urls')),  # будет: /admin/
                  path('dashboard/', include('adminapp.urls')),  # будет: /dashboard/

                  path('', HomeView.as_view(), name='home'),

                  path('shop/', include('shop.urls')),
                  path('auth/', include('user.urls.urls_auth')),
                  path('account/', include('user.urls.urls_account')),
              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# if settings.DEBUG:
#    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
# Если есть MEDIA:
# urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
