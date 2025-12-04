# adminapp/views.py
from django.contrib.auth.mixins import PermissionRequiredMixin  # 🔐 Для защиты
from django.views.generic import TemplateView, ListView
from django.shortcuts import render
from django.contrib.auth.models import User, Group  # Для управления ролями
from shop.models import Product, Order, Review  # Импортируй свои модели
from user.models import UserProfile  # Или CustomUser, если у тебя там данные
from django.db.models import Sum, Count, Avg, Q
from django.utils import timezone
from datetime import timedelta
import json


class AdminDashboardView(PermissionRequiredMixin, TemplateView):
    """
    Главная страница кастомной админки.
    Отображает сводку: выручка, заказы, пользователи, топ-товары.
    """
    permission_required = 'shop.can_view_admin_dashboard'  # 🔐 Пример кастомного разрешения (создай его!)
    template_name = 'admin/dashboard.html'  # <- Шаблон для дашборда

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # --- Примеры данных для дашборда ---
        now = timezone.now()
        last_7_days = now - timedelta(days=7)

        # Общая выручка за последние 7 дней
        revenue = Order.objects.filter(
            created_at__gte=last_7_days,
            status='paid'  # или какое поле означает "оплачено"
        ).aggregate(total=Sum('total_price'))['total'] or 0

        # Количество заказов
        orders_count = Order.objects.filter(created_at__gte=last_7_days).count()

        # Количество новых пользователей
        users_count = UserProfile.objects.filter(date_joined__gte=last_7_days).count() # или User.objects

        # Топ-10 продаваемых товаров
        top_products = Product.objects.filter(
            order_items__order__status='paid',  # или какое поле означает "оплачено"
            order_items__order__created_at__gte=last_7_days
        ).annotate(
            total_sold=Sum('order_items__quantity')  # или как у тебя связаны OrderItem и Product
        ).order_by('-total_sold')[:10]

        context.update({
            'revenue_last_7_days': revenue,
            'orders_count_last_7_days': orders_count,
            'users_count_last_7_days': users_count,
            'top_products': top_products,
        })
        return context


class AdminStatsView(PermissionRequiredMixin, TemplateView):
    """
    Страница с детальной аналитикой (графики и т.п.).
    """
    permission_required = 'shop.can_view_admin_stats'
    template_name = 'admin/stats.html'  # <- Шаблон для статистики

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Пример: данные для графика продаж по дням за месяц
        end_date = timezone.now()
        start_date = end_date - timedelta(days=30)

        sales_data = []
        current_date = start_date
        while current_date <= end_date:
            day_revenue = Order.objects.filter(
                created_at__date=current_date,
                status='paid'
            ).aggregate(total=Sum('total_price'))['total'] or 0
            sales_data.append({'date': current_date.strftime('%Y-%m-%d'), 'revenue': float(day_revenue)})
            current_date += timedelta(days=1)

        # Пример: популярность категорий
        category_sales = Product.objects.filter(
            order_items__order__status='paid'
        ).values('category__name').annotate(
            total_sold=Sum('order_items__quantity')
        ).order_by('-total_sold')

        context.update({
            'sales_chart_data': json.dumps(sales_data),  # для передачи в JS
            'category_popularity': category_sales,
        })
        return context


class AdminSearchView(PermissionRequiredMixin, TemplateView):
    """
    Страница поиска по админке.
    """
    permission_required = 'shop.can_search_admin_panel'
    template_name = 'admin/search.html'  # <- Шаблон для поиска

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = self.request.GET.get('q', '').strip()

        results = {}
        if query:
            # Поиск по продуктам
            results['products'] = Product.objects.filter(
                Q(name__icontains=query) | Q(description__icontains=query)
            )
            # Поиск по заказам (ID, email)
            results['orders'] = Order.objects.filter(
                Q(id__icontains=query) | Q(user__email__icontains=query)
            )
            # Поиск по пользователям
            results['users'] = UserProfile.objects.filter( # или User.objects
                Q(user__username__icontains=query) | Q(user__email__icontains=query)
            )
            # Поиск по отзывам
            results['reviews'] = Review.objects.filter(
                Q(comment__icontains=query) | Q(product__name__icontains=query)
            )

        context['query'] = query
        context['results'] = results
        return context


class AdminPermissionsView(PermissionRequiredMixin, TemplateView):
    """
    Управление ролями и разрешениями.
    """
    permission_required = 'auth.change_permission'  # 🔐 Разрешение на изменение прав (встроено)
    template_name = 'admin/permissions.html'  # <- Шаблон для управления правами

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Получаем пользователей с их группами и правами
        users_with_perms = User.objects.prefetch_related('groups', 'user_permissions').all()

        context.update({
            'users_with_perms': users_with_perms,
            'all_groups': Group.objects.all(),  # для формы добавления в группу
            'all_permissions': Permission.objects.all(), # для формы добавления разрешения
        })
        return context

    def post(self, request, *args, **kwargs):
        # Логика добавления/удаления прав или групп
        # ...
        # Пример: добавить пользователя в группу
        user_id = request.POST.get('user_id')
        group_id = request.POST.get('group_id')
        action = request.POST.get('action') # 'add' или 'remove'

        if user_id and group_id and action:
            user = get_object_or_404(User, id=user_id)
            group = get_object_or_404(Group, id=group_id)

            if action == 'add':
                user.groups.add(group)
                messages.success(request, f"User {user.username} added to group {group.name}")
            elif action == 'remove':
                user.groups.remove(group)
                messages.success(request, f"User {user.username} removed from group {group.name}")

        return self.get(request, *args, **kwargs) # Обновляем страницу