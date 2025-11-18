from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .forms import RegistrationForm, LoginForm, OrderConfirmationForm
from .models import Product, Cart, CartItem, Order, OrderItem

@login_required
def profile(request):
    orders = Order.objects.filter(user=request.user).prefetch_related(
        'orderitem_set__product'
    ).order_by('-created_at')
    
    return render(request, 'profile.html', {
        'orders': orders
    })

@login_required
@require_POST
def cancel_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    if order.status == 'pending':
        # Возвращаем товары на склад
        for order_item in order.orderitem_set.all():
            product = order_item.product
            product.stock_quantity += order_item.quantity
            product.in_stock = True
            product.save()
        
        order.status = 'cancelled'
        order.save()
        return JsonResponse({
            'success': True, 
            'message': f'Заказ #{order.id} успешно отменен! Товары возвращены на склад.'
        })
    else:
        return JsonResponse({
            'success': False,
            'message': 'Невозможно отменить заказ в текущем статусе'
        })

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
    products = Product.objects.filter(in_stock=True)
    context = {
        'products': products,
    }
    return render(request, 'catalog.html', context)

def product_detail(request, product_id):
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
        
        errors = {}
        for field, error_list in form.errors.items():
            errors[field] = error_list[0]
        
        return JsonResponse({
            'success': False, 
            'errors': errors
        })
    
    else:
        form = LoginForm()
    return render(request, 'registration/login.html', {'form': form})

@login_required
def cart_view(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_items = cart.items.all()
    
    if request.method == 'POST':
        form = OrderConfirmationForm(request.POST, user=request.user)
        if form.is_valid():
            # Проверяем, что все товары есть в достаточном количестве
            for cart_item in cart_items:
                if cart_item.quantity > cart_item.product.stock_quantity:
                    return JsonResponse({
                        'success': False,
                        'message': f'Недостаточно товара "{cart_item.product.name}" на складе. Доступно: {cart_item.product.stock_quantity} шт.'
                    })
            
            # Создаем заказ
            order = Order.objects.create(
                user=request.user,
                total_price=cart.get_total_price(),
                status='pending'
            )
            
            # Переносим товары из корзины в заказ и уменьшаем количество на складе
            for cart_item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    quantity=cart_item.quantity,
                    price=cart_item.product.price
                )
                
                # Уменьшаем количество товара на складе
                product = cart_item.product
                product.stock_quantity -= cart_item.quantity
                
                if product.stock_quantity <= 0:
                    product.in_stock = False
                    product.stock_quantity = 0
                
                product.save()
            
            # Очищаем корзину
            cart.items.all().delete()
            
            return JsonResponse({
                'success': True, 
                'message': f'Заказ #{order.id} успешно создан!',
                'order_id': order.id
            })
        else:
            errors = {field: error[0] for field, error in form.errors.items()}
            return JsonResponse({'success': False, 'errors': errors})
    
    form = OrderConfirmationForm(user=request.user)
    
    context = {
        'cart': cart,
        'cart_items': cart_items,
        'form': form,
    }
    return render(request, 'cart.html', context)

@login_required
@require_POST
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id, in_stock=True)
    cart, created = Cart.objects.get_or_create(user=request.user)
    
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={'quantity': 1}
    )
    
    if not created:
        if cart_item.quantity + 1 > product.stock_quantity:
            return JsonResponse({
                'success': False,
                'message': f'Нельзя добавить больше {product.stock_quantity} единиц товара. В корзине уже {cart_item.quantity} шт.'
            })
        cart_item.quantity += 1
        cart_item.save()
    
    return JsonResponse({
        'success': True,
        'message': 'Товар добавлен в корзину',
        'cart_total': cart.get_total_quantity(),
        'item_quantity': cart_item.quantity
    })

@login_required
@require_POST
def remove_from_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart = get_object_or_404(Cart, user=request.user)
    
    try:
        cart_item = CartItem.objects.get(cart=cart, product=product)
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
            message = 'Количество товара уменьшено'
        else:
            cart_item.delete()
            message = 'Товар удален из корзины'
        
        return JsonResponse({
            'success': True,
            'message': message,
            'cart_total': cart.get_total_quantity(),
            'item_quantity': cart_item.quantity if cart_item.quantity > 0 else 0
        })
    except CartItem.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Товар не найден в корзине'
        })

@login_required
@require_POST
def delete_from_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart = get_object_or_404(Cart, user=request.user)
    
    try:
        cart_item = CartItem.objects.get(cart=cart, product=product)
        cart_item.delete()
        
        return JsonResponse({
            'success': True,
            'message': 'Товар удален из корзины',
            'cart_total': cart.get_total_quantity()
        })
    except CartItem.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Товар не найден в корзине'
        })
@login_required
def profile(request):
    orders = Order.objects.filter(user=request.user).prefetch_related(
        'orderitem_set__product'
    ).order_by('-created_at')
    
    return render(request, 'profile.html', {
        'orders': orders
    })