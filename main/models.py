from django.db import models
from django.contrib.auth.models import AbstractUser
import re
from django.core.exceptions import ValidationError

class CustomUser(AbstractUser):
    patronymic = models.CharField(
        max_length=50, 
        blank=True, 
        null=True, 
        verbose_name='Отчество'
    )
    
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        related_name='customuser_set',
        related_query_name='customuser',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
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
    country = models.CharField(max_length=100, verbose_name='Страна производства', default='Россия')
    model = models.CharField(max_length=100, verbose_name='Модель', blank=True)
    in_stock = models.BooleanField(default=True, verbose_name='В наличии')
    stock_quantity = models.IntegerField(default=10, verbose_name='Количество на складе')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата добавления')

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        """При сохранении автоматически обновляем поле in_stock"""
        self.in_stock = self.stock_quantity > 0
        super().save(*args, **kwargs)

class Cart(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, verbose_name='Пользователь')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')

    class Meta:
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзины'

    def __str__(self):
        return f'Корзина пользователя {self.user.username}'

    def get_total_price(self):
        return sum(item.get_total_price() for item in self.items.all())

    def get_total_quantity(self):
        return sum(item.quantity for item in self.items.all())

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items', verbose_name='Корзина')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='Товар')
    quantity = models.PositiveIntegerField(default=1, verbose_name='Количество')

    class Meta:
        verbose_name = 'Элемент корзины'
        verbose_name_plural = 'Элементы корзины'
        unique_together = ['cart', 'product']

    def __str__(self):
        return f'{self.product.name} x {self.quantity}'

    def get_total_price(self):
        return self.product.price * self.quantity

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Ожидает обработки'),
        ('processing', 'В обработке'),
        ('completed', 'Завершен'),
        ('cancelled', 'Отменен'),
    ]

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, verbose_name='Пользователь')
    items = models.ManyToManyField(Product, through='OrderItem', verbose_name='Товары')
    total_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Общая стоимость')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='Статус')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
        ordering = ['-created_at']

    def __str__(self):
        return f'Заказ #{self.id} от {self.user.username}'

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, verbose_name='Заказ')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='Товар')
    quantity = models.PositiveIntegerField(verbose_name='Количество')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена на момент заказа')

    class Meta:
        verbose_name = 'Элемент заказа'
        verbose_name_plural = 'Элементы заказа'

    def __str__(self):
        return f'{self.product.name} x {self.quantity}'