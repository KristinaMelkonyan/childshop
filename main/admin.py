from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

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