from django.shortcuts import render
from django.views import generic


class AdminDashboardView(generic.TemplateView):
    pass

class AdminStatsView(generic.TemplateView):
    pass


class AdminSearchView(generic.TemplateView):
    pass


class AdminPermissionsView(generic.TemplateView):
    pass
