from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from .models import Product, Tag, Seller, Client, ProductPhoto, CartItem


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['id', 'tagtitle', 'products_count', 'created_at']
    search_fields = ['tagtitle']
    list_filter = ['created_at']
    ordering = ['tagtitle']
    
    def products_count(self, obj):
        """Количество продуктов с этим тегом"""
        return obj.products.count()
    products_count.short_description = 'Количество продуктов'


@admin.register(Seller)
class SellerAdmin(BaseUserAdmin):
    """Админка для продавцов с возможностью создания и управления паролями"""
    list_display = ['id', 'email', 'company_name', 'contact_person', 'phone', 'products_count', 'is_active', 'date_joined']
    search_fields = ['email', 'company_name', 'contact_person']
    list_filter = ['is_active', 'is_staff', 'date_joined']
    readonly_fields = ['date_joined', 'last_login']
    ordering = ['-date_joined']
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Основная информация'), {
            'fields': ('company_name', 'contact_person', 'phone'),
            'description': 'Контактная информация продавца'
        }),
        (_('Права доступа'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Важные даты'), {
            'fields': ('last_login', 'date_joined'),
            'description': 'Дата регистрации и последнего входа'
        }),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'company_name', 'contact_person', 'phone'),
            'description': 'Создание нового продавца. Пароль будет автоматически захеширован.'
        }),
    )
    
    def products_count(self, obj):
        """Количество продуктов продавца"""
        if obj.pk:
            return obj.products.count()
        return 0
    products_count.short_description = 'Продуктов'


@admin.register(Client)
class ClientAdmin(BaseUserAdmin):
    """Админка для клиентов с возможностью создания и управления паролями"""
    list_display = ['id', 'email', 'first_name', 'last_name', 'phone', 'is_active', 'date_joined']
    search_fields = ['email', 'first_name', 'last_name']
    list_filter = ['is_active', 'is_staff', 'date_joined']
    readonly_fields = ['date_joined', 'last_login']
    ordering = ['-date_joined']
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Основная информация'), {
            'fields': ('first_name', 'last_name', 'phone'),
            'description': 'Личная информация клиента'
        }),
        (_('Права доступа'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Важные даты'), {
            'fields': ('last_login', 'date_joined'),
            'description': 'Дата регистрации и последнего входа'
        }),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'first_name', 'last_name', 'phone'),
            'description': 'Создание нового клиента. Пароль будет автоматически захеширован.'
        }),
    )


class ProductPhotoInline(admin.TabularInline):
    """Inline для загрузки фотографий продукта"""
    model = ProductPhoto
    extra = 1
    fields = ('photo', 'order')
    verbose_name = 'Фотография'
    verbose_name_plural = 'Фотографии продукта'


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'title', 'price', 'stock', 'seller', 'checked', 
        'created_at', 'thumbnail_preview', 'photos_count'
    ]
    list_filter = ['checked', 'created_at', 'seller']
    search_fields = ['title', 'description', 'seller__company_name']
    readonly_fields = ['created_at', 'updated_at', 'thumbnail_preview', 'photos_count']
    filter_horizontal = ['tags']
    inlines = [ProductPhotoInline]
    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'description', 'seller'),
            'description': 'Название, описание и продавец продукта'
        }),
        ('Цена и наличие', {
            'fields': ('price', 'stock'),
            'description': 'Цена в рублях и количество товара на складе. Цена не может быть отрицательной.'
        }),
        ('Медиа', {
            'fields': ('thumbnail', 'thumbnail_preview', 'photos_count'),
            'description': 'Миниатюра продукта. Фотографии загружаются через раздел "Фотографии продукта" ниже.'
        }),
        ('Дополнительно', {
            'fields': ('tags', 'checked'),
            'description': 'Теги продукта и статус проверки. Только администратор может изменить поле "Проверен".'
        }),
        ('Даты', {
            'fields': ('created_at', 'updated_at'),
            'description': 'Дата создания и последнего обновления продукта'
        }),
    )
    
    def thumbnail_preview(self, obj):
        """Превью миниатюры"""
        if obj.thumbnail:
            return format_html(
                '<img src="{}" style="max-width: 100px; max-height: 100px;" />',
                obj.thumbnail.url
            )
        return "Нет изображения"
    thumbnail_preview.short_description = 'Превью'
    
    def photos_count(self, obj):
        """Количество фотографий"""
        if obj.pk:
            return obj.product_photos.count()
        return 0
    photos_count.short_description = 'Фотографий'
    
    def get_queryset(self, request):
        """Оптимизация запросов"""
        return super().get_queryset(request).select_related('seller').prefetch_related('tags', 'product_photos')


@admin.register(ProductPhoto)
class ProductPhotoAdmin(admin.ModelAdmin):
    """Админка для фотографий продуктов"""
    list_display = ['id', 'product', 'photo_preview', 'order', 'created_at']
    list_filter = ['created_at', 'product']
    search_fields = ['product__title']
    readonly_fields = ['created_at', 'photo_preview']
    ordering = ['product', 'order', 'created_at']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('product', 'photo', 'photo_preview', 'order'),
            'description': 'Выберите продукт и загрузите фотографию. Порядок определяет последовательность отображения.'
        }),
        ('Дата', {
            'fields': ('created_at',),
            'description': 'Дата загрузки фотографии'
        }),
    )
    
    def photo_preview(self, obj):
        """Превью фотографии"""
        if obj.photo:
            return format_html(
                '<img src="{}" style="max-width: 200px; max-height: 200px;" />',
                obj.photo.url
            )
        return "Нет изображения"
    photo_preview.short_description = 'Превью'


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    """Админка для товаров в корзине"""
    list_display = ['id', 'client', 'product', 'quantity', 'total_price', 'created_at']
    list_filter = ['created_at', 'product']
    search_fields = ['client__email', 'product__title']
    readonly_fields = ['created_at', 'updated_at', 'total_price']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('client', 'product', 'quantity'),
            'description': 'Клиент, продукт и количество товара в корзине'
        }),
        ('Даты', {
            'fields': ('created_at', 'updated_at', 'total_price'),
            'description': 'Дата добавления, обновления и общая стоимость'
        }),
    )
    
    def total_price(self, obj):
        """Общая стоимость товара"""
        return f"{obj.get_total_price()} ₽"
    total_price.short_description = 'Общая стоимость'
