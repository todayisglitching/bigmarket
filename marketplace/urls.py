from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from . import auth_views
from . import cart_views
from . import seller_views
from .api_views import (
    ProductViewSet, TagViewSet,
    SellerRegistrationView, ClientRegistrationView,
    SellerProfileView, ClientProfileView
)

# Настройка роутера для API
router = DefaultRouter()
router.register(r'api/products', ProductViewSet, basename='product')
router.register(r'api/tags', TagViewSet, basename='tag')

urlpatterns = [
    # Веб-страницы
    path("", views.index, name="index"),
    path("products/<int:product_id>/", views.product_detail, name="product_detail"),
    
    # Веб-формы аутентификации
    path("auth/client/register/", auth_views.client_register, name="client_register"),
    path("auth/client/login/", auth_views.client_login, name="client_login"),
    path("auth/seller/login/", auth_views.seller_login, name="seller_login"),
    path("auth/logout/", auth_views.logout, name="logout"),
    
    # Корзина
    path("cart/", cart_views.cart_view, name="cart"),
    path("cart/add/<int:product_id>/", cart_views.add_to_cart, name="add_to_cart"),
    path("cart/remove/<int:cart_item_id>/", cart_views.remove_from_cart, name="remove_from_cart"),
    path("cart/update/<int:cart_item_id>/", cart_views.update_cart_item, name="update_cart_item"),
    
    # Панель продавца
    path("seller/dashboard/", seller_views.seller_dashboard, name="seller_dashboard"),
    path("seller/products/", seller_views.seller_products, name="seller_products"),
    path("seller/products/create/", seller_views.seller_product_create, name="seller_product_create"),
    path("seller/products/<int:product_id>/edit/", seller_views.seller_product_edit, name="seller_product_edit"),
    path("seller/products/<int:product_id>/delete/", seller_views.seller_product_delete, name="seller_product_delete"),
    
    # API маршруты
    path('', include(router.urls)),
    
    # API Регистрация (клиенты могут регистрироваться через веб или API)
    path('api/auth/client/register/', ClientRegistrationView.as_view(), name='client_register_api'),
    # Продавцы регистрируются только через БД/админку, но оставляем API для совместимости
    path('api/auth/seller/register/', SellerRegistrationView.as_view(), name='seller_register_api'),
    
    # Профили
    path('api/auth/seller/profile/', SellerProfileView.as_view(), name='seller_profile'),
    path('api/auth/client/profile/', ClientProfileView.as_view(), name='client_profile'),
]
