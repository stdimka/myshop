
from django.urls import path, include
from . import views as admin_views

urlpatterns = [
    path("", admin_views.AdminDashboardView.as_view(), name="admin_dashboard"),
    path("stats/", admin_views.AdminStatsView.as_view(), name="admin_stats"),
    path("search/", admin_views.AdminSearchView.as_view(), name="admin_search"),
    path("permissions/", admin_views.AdminPermissionsView.as_view(), name="admin_permissions"),
]


