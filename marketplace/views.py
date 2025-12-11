from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from .models import Product, Tag


def index(request):
    """
    Главная страница с категориями и продуктами
    """
    # Получаем только проверенные продукты с фотографиями
    products = Product.objects.filter(checked=True).select_related('seller').prefetch_related('tags', 'product_photos')[:12]
    
    # Получаем уникальные теги для категорий
    tags = Tag.objects.all()[:10]
    
    context = {
        'products': products,
        'tags': tags,
    }
    
    return render(request, "marketplace/home.html", context)


def product_detail(request, product_id: int):
    """
    Детальная страница продукта
    """
    product = get_object_or_404(
        Product.objects.select_related('seller').prefetch_related('tags', 'product_photos'),
        id=product_id,
        checked=True  # Только проверенные продукты
    )
    
    # Получаем фотографии продукта, отсортированные по порядку
    photos = product.product_photos.all().order_by('order', 'created_at')
    
    # Похожие продукты (по тегам) с фотографиями
    similar = Product.objects.filter(
        tags__in=product.tags.all(),
        checked=True
    ).exclude(id=product.id).select_related('seller').prefetch_related('tags', 'product_photos').distinct()[:3]
    
    context = {
        'product': product,
        'photos': photos,
        'similar': similar,
    }
    
    return render(request, "marketplace/product_detail.html", context)
