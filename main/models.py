from django.db import models
from django.contrib.auth.models import AbstractUser
import re
from django.core.exceptions import ValidationError
class Product(models.Model):
    CATEGORY_CHOICES = [
        ('plush', 'Плюшевые игрушки'),
        ('constructor', 'Конструкторы'),
        ('doll', 'Куклы'),
        ('educational', 'Развивающие игрушки'),
        ('creative', 'Творческие наборы'),
    ]

    name = models.CharField(max_length=200, verbose_name='Наименование')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена')
    description = models.TextField(verbose_name='Описание', blank=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, verbose_name='Категория')
    image = models.ImageField(upload_to='products/', verbose_name='Изображение', blank=True)
    year = models.IntegerField(verbose_name='Год производства')
    in_stock = models.BooleanField(default=True, verbose_name='В наличии')
    country = models.CharField(max_length=100, verbose_name='Страна производитель', blank=True, null=True) 
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата добавления')

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'
        ordering = ['-created_at']  # По умолчанию новые сверху

    def __str__(self):
        return self.name

class CustomUser(AbstractUser):
    patronymic = models.CharField(
        max_length=50, 
        blank=True, 
        null=True, 
        verbose_name='Отчество',
        validators=[]
    )
    
    # Указываем кастомные related_name
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to.',
        related_name='customuser_set',
        related_query_name='customuser',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name='customuser_permissions_set',
        related_query_name='customuser',
    )
    
    def clean(self):
        if self.first_name and not re.match(r'^[а-яА-ЯёЁ\s-]+$', self.first_name):
            raise ValidationError({'first_name': 'Имя может содержать только кириллицу, пробелы и тире'})
        if self.last_name and not re.match(r'^[а-яА-ЯёЁ\s-]+$', self.last_name):
            raise ValidationError({'last_name': 'Фамилия может содержать только кириллицу, пробелы и тире'})
        if self.patronymic and not re.match(r'^[а-яА-ЯёЁ\s-]+$', self.patronymic):
            raise ValidationError({'patronymic': 'Отчество может содержать только кириллицу, пробелы и тире'})
        if self.username and not re.match(r'^[a-zA-Z0-9-]+$', self.username):
            raise ValidationError({'username': 'Логин может содержать только латиницу, цифры и тире'})

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'