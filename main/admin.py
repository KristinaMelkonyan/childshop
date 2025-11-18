from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from django.urls import path
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models import Count, Q
from django.http import HttpResponse
import csv
from datetime import datetime
from .models import CustomUser, Category, Product, Cart, CartItem, Order, OrderItem

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'is_active', 'products_count', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    list_editable = ['is_active']
    prepopulated_fields = {'slug': ('name',)}
    
    def products_count(self, obj):
        return obj.product_set.count()
    products_count.short_description = 'Количество товаров'

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'category', 'stock_quantity', 'in_stock', 'is_published', 'created_at']
    list_filter = ['category', 'in_stock', 'is_published', 'created_at']
    search_fields = ['name', 'description', 'model']
    list_editable = ['price', 'stock_quantity', 'is_published']
    actions = ['publish_products', 'unpublish_products']
    
    def publish_products(self, request, queryset):
        updated = queryset.update(is_published=True)
        self.message_user(request, f'{updated} товаров опубликовано')
    publish_products.short_description = 'Опубликовать выбранные товары'
    
    def unpublish_products(self, request, queryset):
        updated = queryset.update(is_published=False)
        self.message_user(request, f'{updated} товаров снято с публикации')
    unpublish_products.short_description = 'Снять с публикации выбранные товары'

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'patronymic', 'is_staff')
    list_filter = ('is_staff', 'is_superuser', 'is_active')
    fieldsets = UserAdmin.fieldsets + (
        ('Дополнительная информация', {
            'fields': ('patronymic',),
        }),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Дополнительная информация', {
            'fields': ('patronymic',),
        }),
    )

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['product', 'quantity', 'price', 'get_total']
    can_delete = False
    
    def has_add_permission(self, request, obj=None):
        return False
    
    def get_total(self, obj):
        return f"{obj.quantity * obj.price} ₽"
    get_total.short_description = 'Сумма'

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'created_at', 'user_full_name', 'items_count', 'total_price', 'status_badge', 'quick_actions']
    list_filter = ['status', 'created_at']
    search_fields = ['user__username', 'user__email', 'user__first_name', 'user__last_name', 'user__patronymic']
    readonly_fields = ['created_at', 'updated_at', 'order_details', 'user_info']
    list_editable = []
    actions = ['confirm_selected_orders', 'complete_selected_orders', 'cancel_selected_orders', 'export_orders_csv']
    inlines = [OrderItemInline]
    list_per_page = 20
    
    # Кастомные фильтры для статусов
    class StatusFilter(admin.SimpleListFilter):
        title = 'Статус заказа'
        parameter_name = 'status'
        
        def lookups(self, request, model_admin):
            return [
                ('new', 'Новые'),
                ('processing', 'Подтвержденные'),
                ('completed', 'Завершенные'),
                ('cancelled', 'Отмененные'),
            ]
        
        def queryset(self, request, queryset):
            if self.value() == 'new':
                return queryset.filter(status='pending')
            elif self.value() == 'processing':
                return queryset.filter(status='processing')
            elif self.value() == 'completed':
                return queryset.filter(status='completed')
            elif self.value() == 'cancelled':
                return queryset.filter(status='cancelled')
            return queryset
    
    list_filter = [StatusFilter, 'created_at']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('user_info', 'total_price', 'status', 'cancellation_reason')
        }),
        ('Даты', {
            'fields': ('created_at', 'updated_at')
        }),
        ('Детали заказа', {
            'fields': ('order_details',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user').prefetch_related('orderitem_set')
    
    def user_full_name(self, obj):
        return obj.get_user_full_name()
    user_full_name.short_description = 'ФИО заказчика'
    user_full_name.admin_order_field = 'user__last_name'
    
    def items_count(self, obj):
        count = obj.get_items_count()
        return format_html(
            '<span style="font-weight: bold; color: #E91E63;">{}</span>',
            f"{count} шт."
        )
    items_count.short_description = 'Товаров'
    
    def status_badge(self, obj):
        status_config = {
            'pending': {'color': '#FF9800', 'text': 'Новый', 'icon': '⏰'},
            'processing': {'color': '#2196F3', 'text': 'Подтвержден', 'icon': '✅'},
            'completed': {'color': '#4CAF50', 'text': 'Завершен', 'icon': '🏁'},
            'cancelled': {'color': '#F44336', 'text': 'Отменен', 'icon': '❌'},
        }
        config = status_config.get(obj.status, {'color': '#666', 'text': obj.status, 'icon': ''})
        
        return format_html(
            '<span style="background: {}; color: white; padding: 4px 8px; border-radius: 12px; font-size: 12px; font-weight: bold; display: inline-flex; align-items: center; gap: 4px;">{} {}</span>',
            config['color'],
            config['icon'],
            config['text']
        )
    status_badge.short_description = 'Статус'
    status_badge.admin_order_field = 'status'
    
    def quick_actions(self, obj):
        actions = []
        if obj.status == 'pending':
            actions.append(
                format_html(
                    '<a href="{}" class="button" style="background: #4CAF50; color: white; padding: 4px 8px; border-radius: 4px; text-decoration: none; font-size: 12px; margin-right: 4px;">Подтвердить</a>',
                    f"{obj.id}/confirm/"
                )
            )
            actions.append(
                format_html(
                    '<a href="{}" class="button" style="background: #F44336; color: white; padding: 4px 8px; border-radius: 4px; text-decoration: none; font-size: 12px;">Отменить</a>',
                    f"{obj.id}/cancel/"
                )
            )
        elif obj.status == 'processing':
            actions.append(
                format_html(
                    '<a href="{}" class="button" style="background: #2196F3; color: white; padding: 4px 8px; border-radius: 4px; text-decoration: none; font-size: 12px;">Завершить</a>',
                    f"{obj.id}/complete/"
                )
            )
        
        if not actions:
            return format_html('<span style="color: #999;">—</span>')
        
        return format_html(''.join(actions))
    quick_actions.short_description = 'Действия'
    
    def user_info(self, obj):
        user = obj.user
        return format_html(
            '<div style="padding: 10px; background: #f8f9fa; border-radius: 5px;">'
            '<strong>ФИО:</strong> {} {} {}<br>'
            '<strong>Логин:</strong> {}<br>'
            '<strong>Email:</strong> {}<br>'
            '<strong>Телефон:</strong> {}'
            '</div>',
            user.last_name, user.first_name, user.patronymic or '',
            user.username,
            user.email,
            getattr(user, 'phone', 'не указан')
        )
    user_info.short_description = 'Информация о пользователе'
    
    def order_details(self, obj):
        items = obj.orderitem_set.all()
        if items:
            items_html = "<br>".join([
                f"<div style='margin: 5px 0; padding: 5px; background: #f8f9fa; border-radius: 3px;'>"
                f"<strong>{item.product.name}</strong> - {item.quantity} шт. × {item.price} ₽ = <strong>{item.quantity * item.price} ₽</strong>"
                f"</div>" 
                for item in items
            ])
            return format_html(
                '<div style="max-height: 300px; overflow-y: auto;">{}</div>'
                '<div style="margin-top: 10px; padding: 10px; background: #e3f2fd; border-radius: 5px;">'
                '<strong>Итого: {} ₽</strong>'
                '</div>',
                items_html,
                obj.total_price
            )
        return format_html('<div style="color: #999;">Нет товаров</div>')
    order_details.short_description = 'Состав заказа'
    
    # Кастомные действия
    def confirm_selected_orders(self, request, queryset):
        orders = queryset.filter(status='pending')
        count = orders.count()
        if count:
            orders.update(status='processing')
            self.message_user(
                request, 
                f'✅ {count} заказ(ов) подтверждено и переведено в статус "Подтвержден"', 
                messages.SUCCESS
            )
        else:
            self.message_user(
                request, 
                'ℹ️ Нет заказов со статусом "Новый" для подтверждения', 
                messages.WARNING
            )
    confirm_selected_orders.short_description = '✅ Подтвердить выбранные заказы'
    
    def complete_selected_orders(self, request, queryset):
        orders = queryset.filter(status='processing')
        count = orders.count()
        if count:
            orders.update(status='completed')
            self.message_user(
                request, 
                f'🏁 {count} заказ(ов) завершено', 
                messages.SUCCESS
            )
        else:
            self.message_user(
                request, 
                'ℹ️ Нет заказов со статусом "Подтвержден" для завершения', 
                messages.WARNING
            )
    complete_selected_orders.short_description = '🏁 Завершить выбранные заказы'
    
    def cancel_selected_orders(self, request, queryset):
        if 'apply' in request.POST:
            reason = request.POST.get('cancellation_reason', '').strip()
            if not reason:
                self.message_user(request, '❌ Необходимо указать причину отказа', messages.ERROR)
                return
            
            orders = queryset.filter(status='pending')
            count = orders.count()
            if count:
                for order in orders:
                    order.status = 'cancelled'
                    order.cancellation_reason = reason
                    order.save()
                
                self.message_user(
                    request, 
                    f'❌ {count} заказ(ов) отменено с причиной: {reason}', 
                    messages.SUCCESS
                )
            else:
                self.message_user(
                    request, 
                    'ℹ️ Нет заказов со статусом "Новый" для отмены', 
                    messages.WARNING
                )
            return
        
        return render(request, 'admin/cancel_orders.html', {
            'orders': queryset,
            'title': 'Укажите причину отмены заказов',
            'action': 'cancel_selected_orders',
        })
    cancel_selected_orders.short_description = '❌ Отменить выбранные заказы'
    
    def export_orders_csv(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="orders_{datetime.now().strftime("%Y%m%d_%H%M")}.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['ID', 'Дата заказа', 'ФИО заказчика', 'Email', 'Товаров', 'Сумма', 'Статус'])
        
        for order in queryset:
            writer.writerow([
                order.id,
                order.created_at.strftime("%d.%m.%Y %H:%M"),
                order.get_user_full_name(),
                order.user.email,
                order.get_items_count(),
                order.total_price,
                order.get_status_display()
            ])
        
        return response
    export_orders_csv.short_description = '📊 Экспорт в CSV'
    
    # Кастомные URL для быстрых действий
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('<path:object_id>/confirm/', self.admin_site.admin_view(self.confirm_order), name='order_confirm'),
            path('<path:object_id>/complete/', self.admin_site.admin_view(self.complete_order), name='order_complete'),
            path('<path:object_id>/cancel/', self.admin_site.admin_view(self.cancel_order), name='order_cancel'),
        ]
        return custom_urls + urls
    
    def confirm_order(self, request, object_id):
        order = Order.objects.get(id=object_id)
        if order.status == 'pending':
            order.status = 'processing'
            order.save()
            self.message_user(request, f'✅ Заказ #{order.id} подтвержден', messages.SUCCESS)
        return redirect('admin:shop_order_changelist')
    
    def complete_order(self, request, object_id):
        order = Order.objects.get(id=object_id)
        if order.status == 'processing':
            order.status = 'completed'
            order.save()
            self.message_user(request, f'🏁 Заказ #{order.id} завершен', messages.SUCCESS)
        return redirect('admin:shop_order_changelist')
    
    def cancel_order(self, request, object_id):
        order = Order.objects.get(id=object_id)
        if order.status == 'pending':
            order.status = 'cancelled'
            order.cancellation_reason = 'Отменен администратором'
            order.save()
            self.message_user(request, f'❌ Заказ #{order.id} отменен', messages.SUCCESS)
        return redirect('admin:shop_order_changelist')
    
    class Media:
        css = {
            'all': ('admin/css/orders.css',)
        }

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'product', 'quantity', 'price', 'get_total']
    list_filter = ['order__status']
    search_fields = ['product__name', 'order__user__username']
    
    def get_total(self, obj):
        return f"{obj.quantity * obj.price} ₽"
    get_total.short_description = 'Общая стоимость'

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['user', 'created_at', 'updated_at', 'get_total_quantity', 'get_total_price']
    search_fields = ['user__username']
    
    def get_total_quantity(self, obj):
        return obj.get_total_quantity()
    get_total_quantity.short_description = 'Общее количество'
    
    def get_total_price(self, obj):
        return f"{obj.get_total_price()} ₽"
    get_total_price.short_description = 'Общая стоимость'

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ['cart', 'product', 'quantity', 'get_total_price']
    search_fields = ['product__name', 'cart__user__username']
    
    def get_total_price(self, obj):
        return f"{obj.get_total_price()} ₽"
    get_total_price.short_description = 'Общая стоимость'