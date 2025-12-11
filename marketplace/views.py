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


def catalog(request):
    """
    Страница каталога с поиском и фильтрами
    """
    products = Product.objects.filter(checked=True).select_related('seller').prefetch_related('tags', 'product_photos')
    
    # Поиск по названию и описанию
    search_query = request.GET.get('q', '').strip()
    if search_query:
        products = products.filter(
            Q(title__icontains=search_query) | Q(description__icontains=search_query)
        )
    
    # Фильтр по тегам
    # В GET-запросе неотмеченные чекбоксы не отправляются
    # Поэтому selected_tags будет содержать только отмеченные чекбоксы
    tag_ids = request.GET.getlist('tags')
    valid_tag_ids = []
    
    # Преобразуем в список целых чисел
    for tid in tag_ids:
        try:
            tag_id = int(tid)
            if tag_id > 0:  # Проверяем, что ID валидный
                valid_tag_ids.append(tag_id)
        except (ValueError, TypeError):
            continue
    
    # Применяем фильтр только если есть выбранные теги
    if valid_tag_ids:
        products = products.filter(tags__id__in=valid_tag_ids).distinct()
    
    # Фильтр по цене
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price:
        try:
            products = products.filter(price__gte=float(min_price))
        except (ValueError, TypeError):
            pass
    if max_price:
        try:
            products = products.filter(price__lte=float(max_price))
        except (ValueError, TypeError):
            pass
    
    # Фильтр по наличию
    in_stock = request.GET.get('in_stock', '')
    if in_stock == 'true':
        products = products.filter(stock__gt=0)
    
    # Сортировка
    sort_by = request.GET.get('sort', 'newest')
    if sort_by == 'price_asc':
        products = products.order_by('price')
    elif sort_by == 'price_desc':
        products = products.order_by('-price')
    elif sort_by == 'name':
        products = products.order_by('title')
    else:  # newest (по умолчанию)
        products = products.order_by('-created_at')
    
    # Получаем все теги для фильтров с количеством продуктов
    all_tags = Tag.objects.all().order_by('tagtitle')
    
    # Подсчитываем количество продуктов для каждого тега
    tags_with_counts = []
    for tag in all_tags:
        count = Product.objects.filter(checked=True, tags=tag).count()
        if count > 0:
            tags_with_counts.append({
                'tag': tag,
                'count': count
            })
    
    context = {
        'products': products,
        'tags_with_counts': tags_with_counts,
        'search_query': search_query,
        'selected_tags': valid_tag_ids,  # Список только отмеченных тегов из GET-запроса
        'min_price': min_price or '',
        'max_price': max_price or '',
        'in_stock': in_stock,
        'sort_by': sort_by,
    }
    
    return render(request, "marketplace/catalog.html", context)
