from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_protect
from django.db.models import Sum, F
from .models import Product, CartItem, Client


@csrf_protect
@require_http_methods(["GET"])
def cart_view(request):
    """Просмотр корзины клиента"""
    if not request.session.get('client_id'):
        messages.error(request, 'Необходимо войти в систему для просмотра корзины')
        return redirect('client_login')
    
    try:
        client = Client.objects.get(id=request.session['client_id'])
        cart_items = CartItem.objects.filter(client=client).select_related('product', 'product__seller').prefetch_related('product__product_photos')
        
        # Подсчет общей суммы
        total = sum(item.get_total_price() for item in cart_items)
        
        context = {
            'cart_items': cart_items,
            'total': total,
        }
        
        return render(request, 'marketplace/cart.html', context)
    except Client.DoesNotExist:
        messages.error(request, 'Клиент не найден')
        return redirect('client_login')


@csrf_protect
@require_http_methods(["POST"])
def add_to_cart(request, product_id):
    """Добавление товара в корзину"""
    if not request.session.get('client_id'):
        messages.error(request, 'Необходимо войти в систему для добавления товара в корзину')
        return redirect('client_login')
    
    try:
        client = Client.objects.get(id=request.session['client_id'])
        product = get_object_or_404(Product, id=product_id, checked=True)
        
        # Проверяем наличие товара
        if product.stock <= 0:
            messages.error(request, 'Товар отсутствует на складе')
            return redirect('product_detail', product_id=product_id)
        
        quantity = int(request.POST.get('quantity', 1))
        
        if quantity <= 0:
            messages.error(request, 'Количество должно быть больше нуля')
            return redirect('product_detail', product_id=product_id)
        
        if quantity > product.stock:
            messages.error(request, f'Недостаточно товара на складе. Доступно: {product.stock} шт.')
            return redirect('product_detail', product_id=product_id)
        
        # Получаем или создаем товар в корзине
        cart_item, created = CartItem.objects.get_or_create(
            client=client,
            product=product,
            defaults={'quantity': quantity}
        )
        
        if not created:
            # Если товар уже в корзине, увеличиваем количество
            new_quantity = cart_item.quantity + quantity
            if new_quantity > product.stock:
                messages.error(request, f'Недостаточно товара на складе. Доступно: {product.stock} шт.')
                return redirect('product_detail', product_id=product_id)
            cart_item.quantity = new_quantity
            cart_item.save()
            messages.success(request, f'Количество товара в корзине обновлено')
        else:
            messages.success(request, f'Товар "{product.title}" добавлен в корзину')
        
        return redirect('cart')
        
    except Client.DoesNotExist:
        messages.error(request, 'Клиент не найден')
        return redirect('client_login')
    except ValueError:
        messages.error(request, 'Некорректное количество')
        return redirect('product_detail', product_id=product_id)


@csrf_protect
@require_http_methods(["POST"])
def remove_from_cart(request, cart_item_id):
    """Удаление товара из корзины"""
    if not request.session.get('client_id'):
        messages.error(request, 'Необходимо войти в систему')
        return redirect('client_login')
    
    try:
        client = Client.objects.get(id=request.session['client_id'])
        cart_item = get_object_or_404(CartItem, id=cart_item_id, client=client)
        product_title = cart_item.product.title
        cart_item.delete()
        messages.success(request, f'Товар "{product_title}" удален из корзины')
    except Client.DoesNotExist:
        messages.error(request, 'Клиент не найден')
    except CartItem.DoesNotExist:
        messages.error(request, 'Товар не найден в корзине')
    
    return redirect('cart')


@csrf_protect
@require_http_methods(["POST"])
def update_cart_item(request, cart_item_id):
    """Обновление количества товара в корзине"""
    if not request.session.get('client_id'):
        messages.error(request, 'Необходимо войти в систему')
        return redirect('client_login')
    
    try:
        client = Client.objects.get(id=request.session['client_id'])
        cart_item = get_object_or_404(CartItem, id=cart_item_id, client=client)
        
        quantity = int(request.POST.get('quantity', 1))
        
        if quantity <= 0:
            cart_item.delete()
            messages.success(request, 'Товар удален из корзины')
        elif quantity > cart_item.product.stock:
            messages.error(request, f'Недостаточно товара на складе. Доступно: {cart_item.product.stock} шт.')
        else:
            cart_item.quantity = quantity
            cart_item.save()
            messages.success(request, 'Количество обновлено')
            
    except Client.DoesNotExist:
        messages.error(request, 'Клиент не найден')
    except CartItem.DoesNotExist:
        messages.error(request, 'Товар не найден в корзине')
    except ValueError:
        messages.error(request, 'Некорректное количество')
    
    return redirect('cart')
