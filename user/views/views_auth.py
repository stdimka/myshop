from django.views import generic


class RegistrationView(generic.TemplateView):
    pass

class LoginView(generic.TemplateView):
    pass

class LogoutView(generic.TemplateView):
    pass

class EmailVerifyView(generic.TemplateView):
    pass

class ResendVerificationView(generic.TemplateView):
    pass

class PasswordResetView(generic.TemplateView):
    pass

class PasswordResetConfirmView(generic.TemplateView):
    pass

class PasswordChangeView(generic.TemplateView):
    pass


#my first version

#from django.shortcuts import render

# user/views_auth.py
#from django.shortcuts import render
#from django.http import HttpResponse

# Пример временных views для проверки
#def register_view(request):
#    return HttpResponse("Register page")

#def login_view(request):
#    return HttpResponse("Login page")

#def logout_view(request):
#    return HttpResponse("Logout page")

#def profile_view(request):
#    return HttpResponse("Profile page")