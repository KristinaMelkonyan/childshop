# main/management/commands/create_categories.py
from django.core.management.base import BaseCommand
from main.models import Category

class Command(BaseCommand):
    help = 'Создает начальные категории товаров'

    def handle(self, *args, **options):
        categories = [
            {'name': 'Плюшевые игрушки', 'slug': 'plush'},
            {'name': 'Конструкторы', 'slug': 'constructor'},
            {'name': 'Куклы', 'slug': 'doll'},
            {'name': 'Развивающие игрушки', 'slug': 'educational'},
            {'name': 'Творческие наборы', 'slug': 'creative'},
        ]

        for cat_data in categories:
            category, created = Category.objects.get_or_create(
                slug=cat_data['slug'],
                defaults={'name': cat_data['name']}
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Создана категория: {category.name}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'ℹ️ Категория уже существует: {category.name}')
                )