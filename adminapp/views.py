from django.views.generic import TemplateView
from django.shortcuts import render, redirect
from django.contrib.auth.models import User, Group, Permission
from django.contrib import messages


# ============================
# DASHBOARD
# ============================
class AdminDashboardView(TemplateView):
    template_name = "admin/dashboard.html"


# ============================
# STATS
# ============================
class AdminStatsView(TemplateView):
    template_name = "admin/stats.html"


# ============================
# SEARCH
# ============================
class AdminSearchView(TemplateView):
    template_name = "admin/search.html"


# ============================
# PERMISSIONS & ROLES
# ============================
class AdminPermissionsView(TemplateView):
    template_name = "admin/permissions.html"

    def get(self, request, *args, **kwargs):
        users = User.objects.all().prefetch_related("groups")
        groups = Group.objects.all()
        permissions = Permission.objects.select_related("content_type")

        context = {
            "users_with_perms": users,
            "all_groups": groups,
            "all_permissions": permissions,
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        action = request.POST.get("action")

        # ============================
        # ✅ ДОБАВИТЬ / УБРАТЬ ГРУППУ
        # ============================
        if action in ["add", "remove"]:
            user_id = request.POST.get("user_id")
            group_id = request.POST.get("group_id")

            try:
                user = User.objects.get(id=user_id)
                group = Group.objects.get(id=group_id)

                if action == "add":
                    user.groups.add(group)
                    messages.success(request, f"Группа '{group.name}' добавлена пользователю {user.username}")

                elif action == "remove":
                    user.groups.remove(group)
                    messages.success(request, f"Группа '{group.name}' удалена у пользователя {user.username}")

            except (User.DoesNotExist, Group.DoesNotExist):
                messages.error(request, "Ошибка при изменении группы.")

        # ============================
        # ✅ СОЗДАНИЕ НОВОЙ ГРУППЫ
        # ============================
        elif action == "create_group":
            group_name = request.POST.get("group_name")
            permissions_ids = request.POST.getlist("permissions")

            if group_name:
                group, created = Group.objects.get_or_create(name=group_name)

                if permissions_ids:
                    perms = Permission.objects.filter(id__in=permissions_ids)
                    group.permissions.set(perms)

                if created:
                    messages.success(request, f"Группа '{group.name}' успешно создана.")
                else:
                    messages.info(request, f"Группа '{group.name}' уже существует.")

        return redirect("admin_permissions")
