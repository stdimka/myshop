from django.contrib.auth import views as auth_views
from django.contrib.auth.models import User
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils.http import urlsafe_base64_decode
from django.views import generic

from user.models import UserToken
from user import forms
from user.utils import send_email_verification


class LoginView(auth_views.LoginView):
    template_name = "auth/login.html"
    form_class = forms.LoginForm


class LogoutView(auth_views.LogoutView):
    next_page = reverse_lazy("home")


class RegistrationView(generic.FormView):
    template_name = "auth/register.html"
    form_class = forms.RegistrationForm
    success_url = reverse_lazy("home")

    def form_valid(self, form):
        user = form.save()
        send_email_verification(user)
        messages.success(self.request, "Регистрация успешна! Проверьте email для подтверждения.")

        # Сохраняем емейл в сессии, чтобы отправить запрос на повторную отправку подтверждающего емейл
        self.request.session['pending_verification_email'] = user.email

        return super().form_valid(form)


class EmailVerifyView(generic.TemplateView):
    template_name = "auth/email_verify.html"

    def get(self, request, *args, **kwargs):
        token_value = request.GET.get("token")
        if not token_value:
            messages.error(request, "Токен подтверждения не указан.")
            return redirect("home")

        try:
            token = UserToken.objects.get(token=token_value, token_type="email_verify")
        except UserToken.DoesNotExist:
            messages.error(request, "Неверный токен подтверждения.")
            return redirect("home")

        if not token.is_valid():
            messages.error(request, "Токен истёк или был отозван.")
            return redirect("home")

        # Всё ок, подтверждаем email
        token.user.is_active = True  # если вы создаёте пользователей как неактивных до подтверждения
        token.user.save()
        token.revoke()
        messages.success(request, "Email успешно подтвержден!")
        return redirect("auth_login")


class ResendVerificationView(generic.FormView):
    """Повторная отправка емейл со ссылкой на подтверждение регистрации"""

    def get(self, request, *args, **kwargs):
        # Берём email из сессии
        email = request.session.get("pending_verification_email")
        if not email:
            messages.error(request, "Email для повторной отправки не найден.")
            return redirect("auth_login")

        try:
            user = User.objects.get(email=email)
            if user.is_active:
                messages.info(request, "Email уже подтверждён.")
            else:
                send_email_verification(user)
                messages.success(request, "Письмо для подтверждения email отправлено повторно.")
            # Очищаем email из сессии, чтобы не отправлять снова случайно
            request.session.pop("pending_verification_email", None)
        except User.DoesNotExist:
            messages.error(request, "Пользователь с таким email не найден.")

        # Редирект на страницу логина после обработки
        return redirect("auth_login")

""" ============================= Сброс и восстановление пароля ================================ """

class PasswordResetView(auth_views.PasswordResetView):
    template_name = 'auth/password_reset_form.html'
    form_class = forms.MyPasswordResetForm
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        messages.success(self.request, "Инструкции по сбросу пароля отправлены на email")
        return super().form_valid(form)


class PasswordResetConfirmView(generic.FormView):
    form_class = forms.MySetPasswordForm
    template_name = "auth/password_reset_confirm.html"
    success_url = "/"

    def dispatch(self, request, *args, **kwargs):
        self.uidb64 = kwargs.get("uidb64")
        self.token = kwargs.get("token")

        # Получаем пользователя
        try:
            uid = urlsafe_base64_decode(self.uidb64).decode()
            self.user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            self.user = None

        if self.user is None:
            messages.error(request, "Неверная ссылка для сброса пароля")
            return redirect("/password_reset/")

        # Проверяем токен через UserToken
        token_obj = UserToken.objects.filter(
            token=self.token, user=self.user, token_type="password_reset"
        ).first()

        if not token_obj or not token_obj.is_valid():
            messages.error(request, "Ссылка истекла или недействительна")
            return redirect("/password_reset/")

        self.token_obj = token_obj
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        """Передаём user в форму, чтобы SetPasswordForm корректно работала"""
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.user
        return kwargs

    def form_valid(self, form):
        form.save()
        self.token_obj.revoke()
        messages.success(self.request, "Пароль успешно изменён")
        return super().form_valid(form)


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