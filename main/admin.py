from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from django.urls import path
from django.template.response import TemplateResponse
from django.db.models import Count, Q
from .models import CustomUser, Product, Cart, CartItem, Order, OrderItem

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['model', 'name', 'price', 'category', 'year', 'country', 'stock_quantity', 'in_stock', 'created_at']
    list_filter = ['category', 'in_stock', 'year', 'country', 'created_at']
    search_fields = ['name', 'description', 'country', 'model']
    list_editable = ['price', 'stock_quantity', 'in_stock']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related()

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

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user_info', 'total_price', 'items_count', 'status', 'status_badge', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['user__username', 'user__email', 'user__first_name', 'user__last_name']
    readonly_fields = ['created_at', 'updated_at', 'get_order_items']
    list_editable = ['status']  # Теперь status есть в list_display
    actions = ['mark_as_processing', 'mark_as_completed', 'mark_as_cancelled']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('user', 'total_price', 'status', 'cancellation_reason')
        }),
        ('Даты', {
            'fields': ('created_at', 'updated_at')
        }),
        ('Товары в заказе', {
            'fields': ('get_order_items',)
        }),
    )
    
    def user_info(self, obj):
        full_name = obj.user.get_full_name()
        if full_name:
            return f"{full_name} ({obj.user.email})"
        return f"{obj.user.username} ({obj.user.email})"
    user_info.short_description = 'Пользователь'
    
    def items_count(self, obj):
        return obj.orderitem_set.count()
    items_count.short_description = 'Товаров'
    
    def status_badge(self, obj):
        status_colors = {
            'pending': 'status-pending',
            'processing': 'status-processing', 
            'completed': 'status-completed',
            'cancelled': 'status-cancelled',
        }
        return format_html(
            '<span class="{}">{}</span>',
            status_colors.get(obj.status, ''),
            obj.get_status_display()
        )
    status_badge.short_description = 'Статус (цветной)'
    
    def get_order_items(self, obj):
        items = obj.orderitem_set.all()
        if items:
            return format_html("<br>".join([f"• {item.product.name} - {item.quantity} шт. × {item.price} ₽" for item in items]))
        return "Нет товаров"
    get_order_items.short_description = 'Товары в заказе'
    
    def mark_as_processing(self, request, queryset):
        updated = queryset.update(status='processing')
        self.message_user(request, f"{updated} заказов переведено в статус 'В обработке'")
    mark_as_processing.short_description = "Перевести в статус 'В обработке'"
    
    def mark_as_completed(self, request, queryset):
        updated = queryset.update(status='completed')
        self.message_user(request, f"{updated} заказов переведено в статус 'Завершен'")
    mark_as_completed.short_description = "Перевести в статус 'Завершен'"
    
    def mark_as_cancelled(self, request, queryset):
        updated = queryset.update(status='cancelled')
        self.message_user(request, f"{updated} заказов переведено в статус 'Отменен'")
    mark_as_cancelled.short_description = "Перевести в статус 'Отменен'"

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