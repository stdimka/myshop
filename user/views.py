from django.shortcuts import render

# user/views.py
from django.shortcuts import render
from django.http import HttpResponse

# Пример временных views для проверки
def register_view(request):
    return HttpResponse("Register page")

def login_view(request):
    return HttpResponse("Login page")

def logout_view(request):
    return HttpResponse("Logout page")

def profile_view(request):
    return HttpResponse("Profile page")