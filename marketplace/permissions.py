from rest_framework import permissions
from .models import Seller, Client


class IsSeller(permissions.BasePermission):
    """Проверка, что пользователь является продавцом"""
    
    def has_permission(self, request, view):
        return isinstance(request.user, Seller) and request.user.is_authenticated


class IsClient(permissions.BasePermission):
    """Проверка, что пользователь является клиентом"""
    
    def has_permission(self, request, view):
        return isinstance(request.user, Client) and request.user.is_authenticated


class IsSellerOrReadOnly(permissions.BasePermission):
    """Только продавцы могут создавать/редактировать, остальные только читать"""
    
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return isinstance(request.user, Seller) and request.user.is_authenticated


class IsProductOwner(permissions.BasePermission):
    """Проверка, что пользователь является владельцем продукта"""
    
    def has_object_permission(self, request, view, obj):
        if not isinstance(request.user, Seller):
            return False
        return obj.seller == request.user


class IsAdminOrReadOnly(permissions.BasePermission):
    """Только администратор может изменять, остальные только читать"""
    
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_staff
