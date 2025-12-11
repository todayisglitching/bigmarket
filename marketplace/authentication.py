from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from .models import Seller, Client


class TokenAuthentication(BaseAuthentication):
    """
    Кастомная токен-аутентификация для продавцов и клиентов
    """
    
    def authenticate(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        
        if not auth_header.startswith('Token '):
            return None
        
        token = auth_header.split(' ')[1] if len(auth_header.split(' ')) > 1 else None
        
        if not token:
            return None
        
        # Пробуем найти продавца
        try:
            seller = Seller.objects.get(token=token, is_active=True)
            return (seller, None)
        except Seller.DoesNotExist:
            pass
        
        # Пробуем найти клиента
        try:
            client = Client.objects.get(token=token, is_active=True)
            return (client, None)
        except Client.DoesNotExist:
            pass
        
        raise AuthenticationFailed('Неверный токен или пользователь неактивен')
    
    def authenticate_header(self, request):
        return 'Token'
