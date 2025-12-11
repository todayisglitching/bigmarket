from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db.models import Q
from .models import Product, Tag, Seller, Client
from .serializers import (
    ProductListSerializer, ProductDetailSerializer, ProductCreateSerializer,
    TagSerializer, SellerRegistrationSerializer, ClientRegistrationSerializer,
    SellerSerializer, ClientSerializer
)
from .permissions import (
    IsSeller, IsClient, IsSellerOrReadOnly, 
    IsProductOwner, IsAdminOrReadOnly
)
from .authentication import TokenAuthentication


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet для тегов (только чтение)
    """
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [AllowAny]
    authentication_classes = []


class ProductViewSet(viewsets.ModelViewSet):
    """
    ViewSet для продуктов
    - Все могут просматривать проверенные продукты
    - Только продавцы могут создавать/редактировать свои продукты
    - checked может изменить только администратор
    """
    queryset = Product.objects.all()
    permission_classes = [IsSellerOrReadOnly]
    authentication_classes = [TokenAuthentication]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return ProductCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return ProductCreateSerializer
        elif self.action == 'retrieve':
            return ProductDetailSerializer
        return ProductListSerializer
    
    def get_queryset(self):
        """
        Фильтрация продуктов:
        - Для неавторизованных: только checked=True
        - Для клиентов: только checked=True
        - Для продавцов: все свои продукты + все checked=True
        - Для администраторов: все продукты
        """
        queryset = Product.objects.select_related('seller').prefetch_related('tags')
        
        if not self.request.user or not self.request.user.is_authenticated:
            # Неавторизованные пользователи видят только проверенные продукты
            return queryset.filter(checked=True)
        
        if isinstance(self.request.user, Client):
            # Клиенты видят только проверенные продукты
            return queryset.filter(checked=True)
        
        if isinstance(self.request.user, Seller):
            # Продавцы видят свои продукты + все проверенные
            return queryset.filter(
                Q(seller=self.request.user) | Q(checked=True)
            )
        
        # Администраторы видят все
        return queryset
    
    def get_permissions(self):
        """
        Разные права для разных действий
        """
        if self.action in ['list', 'retrieve']:
            permission_classes = [AllowAny]
        elif self.action == 'create':
            permission_classes = [IsSeller]
        elif self.action in ['update', 'partial_update', 'destroy']:
            permission_classes = [IsProductOwner]
        else:
            permission_classes = [IsSellerOrReadOnly]
        
        return [permission() for permission in permission_classes]
    
    def create(self, request, *args, **kwargs):
        """
        Создание продукта (только для продавцов)
        checked всегда устанавливается в False
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        product = serializer.save()
        
        return Response(
            ProductDetailSerializer(product).data,
            status=status.HTTP_201_CREATED
        )
    
    def update(self, request, *args, **kwargs):
        """
        Обновление продукта
        checked нельзя изменить через API (только через админку)
        """
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        
        # Удаляем checked из данных, если он был передан
        if 'checked' in request.data:
            request.data.pop('checked')
        
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        return Response(ProductDetailSerializer(instance).data)
    
    @action(detail=False, methods=['get'], permission_classes=[IsSeller])
    def my_products(self, request):
        """
        Получить все продукты текущего продавца
        """
        products = self.get_queryset().filter(seller=request.user)
        serializer = ProductListSerializer(products, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'], permission_classes=[AllowAny])
    def similar(self, request, pk=None):
        """
        Получить похожие продукты (по тегам)
        """
        product = self.get_object()
        similar = Product.objects.filter(
            tags__in=product.tags.all(),
            checked=True
        ).exclude(id=product.id).distinct()[:5]
        
        serializer = ProductListSerializer(similar, many=True)
        return Response(serializer.data)


class SellerRegistrationView(generics.CreateAPIView):
    """
    Регистрация продавца
    """
    queryset = Seller.objects.all()
    serializer_class = SellerRegistrationSerializer
    permission_classes = [AllowAny]
    authentication_classes = []
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        seller = serializer.save()
        
        return Response({
            'message': 'Продавец успешно зарегистрирован',
            'seller': SellerSerializer(seller).data
        }, status=status.HTTP_201_CREATED)


class ClientRegistrationView(generics.CreateAPIView):
    """
    Регистрация клиента
    """
    queryset = Client.objects.all()
    serializer_class = ClientRegistrationSerializer
    permission_classes = [AllowAny]
    authentication_classes = []
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        client = serializer.save()
        
        return Response({
            'message': 'Клиент успешно зарегистрирован',
            'client': ClientSerializer(client).data
        }, status=status.HTTP_201_CREATED)


class SellerProfileView(generics.RetrieveUpdateAPIView):
    """
    Профиль продавца (просмотр и обновление)
    """
    serializer_class = SellerSerializer
    permission_classes = [IsSeller]
    authentication_classes = [TokenAuthentication]
    
    def get_object(self):
        return self.request.user


class ClientProfileView(generics.RetrieveUpdateAPIView):
    """
    Профиль клиента (просмотр и обновление)
    """
    serializer_class = ClientSerializer
    permission_classes = [IsClient]
    authentication_classes = [TokenAuthentication]
    
    def get_object(self):
        return self.request.user
