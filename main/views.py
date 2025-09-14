from django.shortcuts import render

def home(request):
    slides = [
        {
            'title': 'Добро пожаловать в мир детства!',
            'description': 'Лучшие игрушки для ваших детей',
            'image': 'images/slides/slide1.jpg'
        },
        {
            'title': 'Новые поступления',
            'description': 'Самые популярные новинки сезона',
            'image': 'images/slides/slide2.jpg'
        },
        {
            'title': 'Скидки до 30%',
            'description': 'Специальные предложения для наших покупателей',
            'image': 'images/slides/slide3.jpg'
        }
    ]
    return render(request, 'home.html', {'slides': slides})

def catalog(request):
    products = [
        {
            'name': 'Плюшевый мишка большой',
            'price': '1 499',
            'price_num': 1499,
            'image': 'images/products/toys/teddy-bear.jpg',
            'category': 'plush',
            'year': 2024,
            'in_stock': True
        },
        {
            'name': 'Конструктор LEGO Classic',
            'price': '2 999',
            'price_num': 2999,
            'image': 'images/products/toys/lego.jpg',
            'category': 'constructor',
            'year': 2023,
            'in_stock': True
        },
        {
            'name': 'Кукла с аксессуарами',
            'price': '3 499',
            'price_num': 3499,
            'image': 'images/products/accessories/doll-set.jpg',
            'category': 'doll',
            'year': 2024,
            'in_stock': False
        },
        {
            'name': 'Развивающий коврик',
            'price': '4 999',
            'price_num': 4999,
            'image': 'images/products/toys/playmat.jpg',
            'category': 'educational',
            'year': 2023,
            'in_stock': True
        },
        {
            'name': 'Набор мягких кубиков',
            'price': '899',
            'price_num': 899,
            'image': 'images/products/toys/blocks.jpg',
            'category': 'educational',
            'year': 2024,
            'in_stock': True
        },
        {
            'name': 'Творческий набор для рисования',
            'price': '1 599',
            'price_num': 1599,
            'image': 'images/products/accessories/art-set.jpg',
            'category': 'creative',
            'year': 2023,
            'in_stock': True
        },
        {
            'name': 'Плюшевый зайчик',
            'price': '1 199',
            'price_num': 1199,
            'image': 'images/products/toys/bunny.jpg',
            'category': 'plush',
            'year': 2024,
            'in_stock': True
        },
        {
            'name': 'Деревянный конструктор',
            'price': '2 299',
            'price_num': 2299,
            'image': 'images/products/toys/wooden-constructor.jpg',
            'category': 'constructor',
            'year': 2023,
            'in_stock': False
        }
    ]
    
    return render(request, 'catalog.html', {'products': products})

def contacts(request):
    return render(request, 'contacts.html')