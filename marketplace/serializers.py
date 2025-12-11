from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from .models import Product, Tag, Seller, Client


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для тегов"""
    
    class Meta:
        model = Tag
        fields = ['id', 'tagtitle']
        read_only_fields = ['id']


class ProductListSerializer(serializers.ModelSerializer):
    """Сериализатор для списка продуктов (без деталей)"""
    seller_company = serializers.CharField(source='seller.company_name', read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    
    class Meta:
        model = Product
        fields = [
            'id', 'title', 'description', 'thumbnail', 
            'price', 'stock', 'seller_company', 'tags', 'checked', 
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'checked']


class ProductDetailSerializer(serializers.ModelSerializer):
    """Сериализатор для детального просмотра продукта"""
    seller_company = serializers.CharField(source='seller.company_name', read_only=True)
    seller_email = serializers.EmailField(source='seller.email', read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    tag_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all(),
        source='tags',
        write_only=True,
        required=False
    )
    
    class Meta:
        model = Product
        fields = [
            'id', 'title', 'description', 'thumbnail', 'photos',
            'price', 'stock', 'seller', 'seller_company', 'seller_email',
            'tags', 'tag_ids', 'checked', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'checked', 'seller']
    
    def validate_title(self, value):
        """Валидация названия"""
        if len(value.strip()) < 3:
            raise serializers.ValidationError("Название должно содержать минимум 3 символа")
        return value.strip()
    
    def validate_description(self, value):
        """Валидация описания"""
        if len(value.strip()) < 10:
            raise serializers.ValidationError("Описание должно содержать минимум 10 символов")
        return value.strip()
    
    def validate_photos(self, value):
        """Валидация фотографий"""
        if not isinstance(value, list):
            raise serializers.ValidationError("Фотографии должны быть списком")
        if len(value) > 10:
            raise serializers.ValidationError("Максимум 10 фотографий")
        return value


class ProductCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания продукта (только для продавцов)"""
    tag_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all(),
        source='tags',
        write_only=True,
        required=False
    )
    
    class Meta:
        model = Product
        fields = [
            'title', 'description', 'thumbnail', 'photos', 
            'price', 'stock', 'tag_ids'
        ]
    
    def validate_title(self, value):
        if len(value.strip()) < 3:
            raise serializers.ValidationError("Название должно содержать минимум 3 символа")
        return value.strip()
    
    def validate_description(self, value):
        if len(value.strip()) < 10:
            raise serializers.ValidationError("Описание должно содержать минимум 10 символов")
        return value.strip()
    
    def validate_photos(self, value):
        if not isinstance(value, list):
            raise serializers.ValidationError("Фотографии должны быть списком")
        if len(value) > 10:
            raise serializers.ValidationError("Максимум 10 фотографий")
        return value
    
    def validate_price(self, value):
        """Валидация цены"""
        if value < 0:
            raise serializers.ValidationError("Цена не может быть отрицательной")
        return value
    
    def validate_stock(self, value):
        """Валидация остатка"""
        if value < 0:
            raise serializers.ValidationError("Остаток не может быть отрицательным")
        return value
    
    def create(self, validated_data):
        # seller устанавливается из request.user
        validated_data['seller'] = self.context['request'].user
        validated_data['checked'] = False  # Всегда False при создании
        return super().create(validated_data)


class SellerRegistrationSerializer(serializers.ModelSerializer):
    """Сериализатор для регистрации продавца"""
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    password_confirm = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )
    
    class Meta:
        model = Seller
        fields = [
            'email', 'password', 'password_confirm',
            'company_name', 'contact_person', 'phone'
        ]
        extra_kwargs = {
            'email': {'required': True},
            'company_name': {'required': True},
            'contact_person': {'required': True},
            'phone': {'required': True},
        }
    
    def validate_email(self, value):
        """Проверка уникальности email"""
        if Seller.objects.filter(email=value).exists():
            raise serializers.ValidationError("Продавец с таким email уже существует")
        if Client.objects.filter(email=value).exists():
            raise serializers.ValidationError("Этот email уже используется")
        return value.lower().strip()
    
    def validate_phone(self, value):
        """Валидация телефона"""
        if not value or len(value.strip()) < 10:
            raise serializers.ValidationError("Некорректный номер телефона")
        return value.strip()
    
    def validate(self, attrs):
        """Проверка совпадения паролей"""
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({
                'password_confirm': 'Пароли не совпадают'
            })
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        seller = Seller.objects.create(**validated_data)
        seller.set_password(password)
        seller.save()
        return seller


class ClientRegistrationSerializer(serializers.ModelSerializer):
    """Сериализатор для регистрации клиента"""
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    password_confirm = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )
    
    class Meta:
        model = Client
        fields = [
            'email', 'password', 'password_confirm',
            'first_name', 'last_name', 'phone'
        ]
        extra_kwargs = {
            'email': {'required': True},
            'first_name': {'required': True},
            'last_name': {'required': True},
        }
    
    def validate_email(self, value):
        """Проверка уникальности email"""
        if Client.objects.filter(email=value).exists():
            raise serializers.ValidationError("Клиент с таким email уже существует")
        if Seller.objects.filter(email=value).exists():
            raise serializers.ValidationError("Этот email уже используется")
        return value.lower().strip()
    
    def validate(self, attrs):
        """Проверка совпадения паролей"""
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({
                'password_confirm': 'Пароли не совпадают'
            })
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        client = Client.objects.create(**validated_data)
        client.set_password(password)
        client.save()
        return client


class SellerSerializer(serializers.ModelSerializer):
    """Сериализатор для продавца (без пароля)"""
    products_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Seller
        fields = [
            'id', 'email', 'company_name', 'contact_person',
            'phone', 'date_joined', 'products_count'
        ]
        read_only_fields = ['id', 'date_joined']
    
    def get_products_count(self, obj):
        return obj.products.count()


class ClientSerializer(serializers.ModelSerializer):
    """Сериализатор для клиента (без пароля)"""
    
    class Meta:
        model = Client
        fields = [
            'id', 'email', 'first_name', 'last_name',
            'phone', 'date_joined'
        ]
        read_only_fields = ['id', 'date_joined']
