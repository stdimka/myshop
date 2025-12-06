from django.views import generic
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin


class AccountView(LoginRequiredMixin, TemplateView):
    template_name = "account/account.html"


class ProfileView(generic.TemplateView):
    pass
class OrderHistoryView(generic.TemplateView):
    pass