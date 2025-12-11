from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone
from django.core.validators import MinLengthValidator, MinValueValidator


class UserManager(BaseUserManager):
    """Менеджер для создания пользователей"""
    
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email обязателен')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)


class Seller(AbstractBaseUser, PermissionsMixin):
    """Модель продавца"""
    email = models.EmailField(unique=True, verbose_name='Email')
    company_name = models.CharField(max_length=255, verbose_name='Название компании')
    contact_person = models.CharField(max_length=255, verbose_name='Контактное лицо')
    phone = models.CharField(max_length=20, verbose_name='Телефон')
    is_active = models.BooleanField(default=True, verbose_name='Активен')
    is_staff = models.BooleanField(default=False, verbose_name='Персонал')
    date_joined = models.DateTimeField(default=timezone.now, verbose_name='Дата регистрации')
    
    # Переопределяем поля из PermissionsMixin с уникальными related_name
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='Группы',
        blank=True,
        help_text='Группы, к которым принадлежит этот продавец',
        related_name='seller_set',
        related_query_name='seller',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='Права доступа',
        blank=True,
        help_text='Специфичные права для этого продавца',
        related_name='seller_set',
        related_query_name='seller',
    )
    
    objects = UserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['company_name', 'contact_person']
    
    class Meta:
        verbose_name = 'Продавец'
        verbose_name_plural = 'Продавцы'
        ordering = ['-date_joined']
    
    def __str__(self):
        return f"{self.company_name} ({self.email})"


class Client(AbstractBaseUser, PermissionsMixin):
    """Модель клиента (покупателя)"""
    email = models.EmailField(unique=True, verbose_name='Email')
    first_name = models.CharField(max_length=150, verbose_name='Имя')
    last_name = models.CharField(max_length=150, verbose_name='Фамилия')
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name='Телефон')
    is_active = models.BooleanField(default=True, verbose_name='Активен')
    is_staff = models.BooleanField(default=False, verbose_name='Персонал')
    date_joined = models.DateTimeField(default=timezone.now, verbose_name='Дата регистрации')
    
    # Переопределяем поля из PermissionsMixin с уникальными related_name
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='Группы',
        blank=True,
        help_text='Группы, к которым принадлежит этот клиент',
        related_name='client_set',
        related_query_name='client',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='Права доступа',
        blank=True,
        help_text='Специфичные права для этого клиента',
        related_name='client_set',
        related_query_name='client',
    )
    
    objects = UserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    
    class Meta:
        verbose_name = 'Клиент'
        verbose_name_plural = 'Клиенты'
        ordering = ['-date_joined']
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"


class Tag(models.Model):
    """Модель тега"""
    tagtitle = models.CharField(
        max_length=100, 
        unique=True, 
        verbose_name='Название тега',
        validators=[MinLengthValidator(2)]
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    
    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ['tagtitle']
    
    def __str__(self):
        return self.tagtitle


class Product(models.Model):
    """Модель продукта"""
    title = models.CharField(
        max_length=255, 
        verbose_name='Название',
        validators=[MinLengthValidator(3)]
    )
    description = models.TextField(verbose_name='Описание')
    thumbnail = models.ImageField(
        upload_to='products/thumbnails/',
        verbose_name='Миниатюра',
        blank=True,
        null=True
    )
    # Поле photos оставлено для обратной совместимости, но рекомендуется использовать ProductPhoto
    photos = models.JSONField(
        default=list,
        verbose_name='Фотографии (устаревшее)',
        help_text='Список URL фотографий (используйте загрузку файлов через админку)',
        blank=True
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        verbose_name='Цена',
        help_text='Цена в рублях',
        validators=[MinValueValidator(0)]
    )
    stock = models.PositiveIntegerField(
        default=0,
        verbose_name='Остаток',
        help_text='Количество товара на складе'
    )
    seller = models.ForeignKey(
        Seller,
        on_delete=models.CASCADE,
        related_name='products',
        verbose_name='Продавец'
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='products',
        blank=True,
        verbose_name='Теги'
    )
    checked = models.BooleanField(
        default=False,
        verbose_name='Проверен',
        help_text='Только администратор может изменить это поле'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')
    
    class Meta:
        verbose_name = 'Продукт'
        verbose_name_plural = 'Продукты'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['checked']),
        ]
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        # Проверяем, что checked может быть изменен только администратором
        # Это будет дополнительно проверяться в сериализаторе и представлениях
        super().save(*args, **kwargs)


class ProductPhoto(models.Model):
    """Модель для фотографий продукта"""
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='product_photos',
        verbose_name='Продукт'
    )
    photo = models.ImageField(
        upload_to='products/photos/',
        verbose_name='Фотография'
    )
    order = models.PositiveIntegerField(
        default=0,
        verbose_name='Порядок',
        help_text='Порядок отображения фотографии (0 - первая)'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата загрузки')
    
    class Meta:
        verbose_name = 'Фотография продукта'
        verbose_name_plural = 'Фотографии продуктов'
        ordering = ['order', 'created_at']
        indexes = [
            models.Index(fields=['product', 'order']),
        ]
    
    def __str__(self):
        return f"Фото {self.order + 1} для {self.product.title}"


class CartItem(models.Model):
    """Модель для товаров в корзине клиента"""
    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        related_name='cart_items',
        verbose_name='Клиент'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='cart_items',
        verbose_name='Продукт'
    )
    quantity = models.PositiveIntegerField(
        default=1,
        verbose_name='Количество',
        help_text='Количество товара в корзине'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата добавления')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')
    
    class Meta:
        verbose_name = 'Товар в корзине'
        verbose_name_plural = 'Товары в корзине'
        unique_together = ['client', 'product']  # Один товар - одна запись в корзине
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['client', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.client.email} - {self.product.title} (x{self.quantity})"
    
    def get_total_price(self):
        """Получить общую стоимость товара (цена * количество)"""
        return self.product.price * self.quantity
