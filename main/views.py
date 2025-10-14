from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .forms import RegistrationForm, LoginForm
from django.shortcuts import render, get_object_or_404
from .models import Product

@login_required
def profile(request):
    return render(request, 'profile.html')

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
    # ФИЛЬТРУЕМ ТОЛЬКО ТОВАРЫ В НАЛИЧИИ
    products = Product.objects.filter(in_stock=True)
    
    context = {
        'products': products,
    }
    return render(request, 'catalog.html', context)

def product_detail(request, product_id):
    # ТОЖЕ ФИЛЬТРУЕМ ТОЛЬКО ТОВАРЫ В НАЛИЧИИ
    product = get_object_or_404(Product, id=product_id, in_stock=True)
    return render(request, 'product_detail.html', {'product': product})

def contacts(request):
    return render(request, 'contacts.html')

def register_view(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return JsonResponse({'success': True, 'message': 'Регистрация успешна!'})
        else:
            errors = {field: error[0] for field, error in form.errors.items()}
            return JsonResponse({'success': False, 'errors': errors})
    
    form = RegistrationForm()
    return render(request, 'registration/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return JsonResponse({
                    'success': True, 
                    'message': 'Вход выполнен успешно!'
                })
        
        # Если форма не валидна, возвращаем ошибки
        errors = {}
        for field, error_list in form.errors.items():
            errors[field] = error_list[0]  # Берем первую ошибку для каждого поля
        
        return JsonResponse({
            'success': False, 
            'errors': errors
        })
    
    else:
        form = LoginForm()
    return render(request, 'registration/login.html', {'form': form})

@login_required
def profile_view(request):
    return render(request, 'registration/profile.html')