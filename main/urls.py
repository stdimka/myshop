from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from django.contrib import admin

from shop.views import HomeView

urlpatterns = [
                  path('administrator/', admin.site.urls),

                  path('admin/', include('adminapp.urls')),  # будет: /admin/

                  path('', HomeView.as_view(), name='home'),

                  path('shop/', include('shop.urls')),
                  path('auth/', include('user.urls.urls_auth')),
                  path('account/', include('user.urls.urls_account')),

                  path("contact/", TemplateView.as_view(template_name="contact.html"), name="contact"),
                  path("faq/", TemplateView.as_view(template_name="faq.html"), name="faq"),
                  path("community/", TemplateView.as_view(template_name="community.html"), name="community"),
                  path("license/", TemplateView.as_view(template_name="license.html"), name="license"),
              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


