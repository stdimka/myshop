from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import UserProfile


class UserProfileInline(admin.StackedInline):  # или TabularInline
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'


class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)

# Сначала нужно "отрегистировать" стандартный User и зарегистрировать свой
admin.site.unregister(User)
admin.site.register(User, UserAdmin)