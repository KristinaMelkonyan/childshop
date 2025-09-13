from django.shortcuts import render

def home(request):
    slides = [
        {
            'title': 'Добро пожаловать в мир детства!',
            'description': 'Лучшие игрушки для ваших детей',
            'image': 'slide1.jpg'
        },
        {
            'title': 'Новые поступления',
            'description': 'Самые популярные новинки сезона',
            'image': 'slide2.jpg'
        },
        {
            'title': 'Скидки до 30%',
            'description': 'Специальные предложения для наших покупателей',
            'image': 'slide3.jpg'
        }
    ]
    return render(request, 'home.html', {'slides': slides})

def catalog(request):
    return render(request, 'catalog.html')

def contacts(request):
    return render(request, 'contacts.html')