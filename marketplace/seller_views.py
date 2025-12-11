from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_protect
from django.db.models import Count, Q
from .models import Seller, Product, Tag
from .forms import ProductForm


@csrf_protect
@require_http_methods(["GET"])
def seller_dashboard(request):
    """Панель управления продавца"""
    if not request.session.get('seller_id'):
        messages.error(request, 'Необходимо войти как продавец')
        return redirect('seller_login')
    
    try:
        seller = Seller.objects.get(id=request.session['seller_id'])
        
        # Статистика
        total_products = Product.objects.filter(seller=seller).count()
        checked_products = Product.objects.filter(seller=seller, checked=True).count()
        unchecked_products = Product.objects.filter(seller=seller, checked=False).count()
        
        # Последние продукты
        recent_products = Product.objects.filter(seller=seller).order_by('-created_at')[:5]
        
        # Продукты с низким остатком
        low_stock_products = Product.objects.filter(
            seller=seller,
            stock__lte=10,
            stock__gt=0
        ).order_by('stock')[:5]
        
        # Продукты без остатка
        out_of_stock_products = Product.objects.filter(
            seller=seller,
            stock=0
        )[:5]
        
        context = {
            'seller': seller,
            'total_products': total_products,
            'checked_products': checked_products,
            'unchecked_products': unchecked_products,
            'recent_products': recent_products,
            'low_stock_products': low_stock_products,
            'out_of_stock_products': out_of_stock_products,
        }
        
        return render(request, 'marketplace/seller/dashboard.html', context)
        
    except Seller.DoesNotExist:
        messages.error(request, 'Продавец не найден')
        return redirect('seller_login')


@csrf_protect
@require_http_methods(["GET"])
def seller_products(request):
    """Список продуктов продавца"""
    if not request.session.get('seller_id'):
        messages.error(request, 'Необходимо войти как продавец')
        return redirect('seller_login')
    
    try:
        seller = Seller.objects.get(id=request.session['seller_id'])
        products = Product.objects.filter(seller=seller).select_related('seller').prefetch_related('tags', 'product_photos').order_by('-created_at')
        
        # Фильтрация
        status_filter = request.GET.get('status', 'all')
        if status_filter == 'checked':
            products = products.filter(checked=True)
        elif status_filter == 'unchecked':
            products = products.filter(checked=False)
        
        context = {
            'seller': seller,
            'products': products,
            'status_filter': status_filter,
        }
        
        return render(request, 'marketplace/seller/products.html', context)
        
    except Seller.DoesNotExist:
        messages.error(request, 'Продавец не найден')
        return redirect('seller_login')


@csrf_protect
@require_http_methods(["GET", "POST"])
def seller_product_create(request):
    """Создание нового продукта продавцом"""
    if not request.session.get('seller_id'):
        messages.error(request, 'Необходимо войти как продавец')
        return redirect('seller_login')
    
    try:
        seller = Seller.objects.get(id=request.session['seller_id'])
        
        if request.method == 'POST':
            form = ProductForm(request.POST, request.FILES)
            if form.is_valid():
                product = form.save(commit=False)
                product.seller = seller
                product.checked = False  # Всегда False при создании
                product.save()
                form.save_m2m()  # Сохраняем теги
                messages.success(request, f'Продукт "{product.title}" успешно создан и отправлен на проверку')
                return redirect('seller_products')
        else:
            form = ProductForm()
        
        context = {
            'seller': seller,
            'form': form,
            'title': 'Создать продукт'
        }
        
        return render(request, 'marketplace/seller/product_form.html', context)
        
    except Seller.DoesNotExist:
        messages.error(request, 'Продавец не найден')
        return redirect('seller_login')


@csrf_protect
@require_http_methods(["GET", "POST"])
def seller_product_edit(request, product_id):
    """Редактирование продукта продавцом"""
    if not request.session.get('seller_id'):
        messages.error(request, 'Необходимо войти как продавец')
        return redirect('seller_login')
    
    try:
        seller = Seller.objects.get(id=request.session['seller_id'])
        product = get_object_or_404(Product, id=product_id, seller=seller)
        
        if request.method == 'POST':
            form = ProductForm(request.POST, request.FILES, instance=product)
            if form.is_valid():
                product = form.save(commit=False)
                # checked не изменяется через форму
                product.save()
                form.save_m2m()  # Сохраняем теги
                messages.success(request, f'Продукт "{product.title}" успешно обновлен')
                return redirect('seller_products')
        else:
            form = ProductForm(instance=product)
        
        context = {
            'seller': seller,
            'form': form,
            'product': product,
            'title': 'Редактировать продукт'
        }
        
        return render(request, 'marketplace/seller/product_form.html', context)
        
    except Seller.DoesNotExist:
        messages.error(request, 'Продавец не найден')
        return redirect('seller_login')


@csrf_protect
@require_http_methods(["POST"])
def seller_product_delete(request, product_id):
    """Удаление продукта продавцом"""
    if not request.session.get('seller_id'):
        messages.error(request, 'Необходимо войти как продавец')
        return redirect('seller_login')
    
    try:
        seller = Seller.objects.get(id=request.session['seller_id'])
        product = get_object_or_404(Product, id=product_id, seller=seller)
        product_title = product.title
        product.delete()
        messages.success(request, f'Продукт "{product_title}" удален')
    except Seller.DoesNotExist:
        messages.error(request, 'Продавец не найден')
    except Product.DoesNotExist:
        messages.error(request, 'Продукт не найден')
    
    return redirect('seller_products')
