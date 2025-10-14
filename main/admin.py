from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Product

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'category', 'year', 'in_stock', 'created_at']
    list_filter = ['category', 'in_stock', 'year', 'created_at']
    search_fields = ['name', 'description']
    list_editable = ['price', 'in_stock']  # Эти поля должны быть в list_display

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    # Добавляем отчество в поля для отображения
    list_display = ('username', 'email', 'first_name', 'last_name', 'patronymic', 'is_staff')
    list_filter = ('is_staff', 'is_superuser', 'is_active')
    
    # Добавляем отчество в fieldsets для формы редактирования
    fieldsets = UserAdmin.fieldsets + (
        ('Дополнительная информация', {
            'fields': ('patronymic',),
        }),
    )
    
    # Добавляем отчество в fieldsets для формы создания
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Дополнительная информация', {
            'fields': ('patronymic',),
        }),
    )