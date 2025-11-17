from adminapp import views as admin_views

admin_urls = [
    ("admin", admin_views.AdminDashboardView, "???", 200),
    ("admin_stats", admin_views.AdminStatsView, "???", 200),
    ("admin_search", admin_views.AdminSearchView, "???", 200),
    ("admin_permissions", admin_views.AdminPermissionsView, "???", 200),
]