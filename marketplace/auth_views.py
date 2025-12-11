from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth import authenticate
from .forms import ClientRegistrationForm, ClientLoginForm, SellerLoginForm
from .models import Client, Seller


@csrf_protect
@require_http_methods(["GET", "POST"])
def client_register(request):
    """Регистрация клиента"""
    if request.method == 'POST':
        form = ClientRegistrationForm(request.POST)
        if form.is_valid():
            client = form.save()
            messages.success(
                request, 
                f'Регистрация успешна! Теперь вы можете войти в систему.'
            )
            return redirect('client_login')
    else:
        form = ClientRegistrationForm()
    
    return render(request, 'marketplace/auth/client_register.html', {
        'form': form,
        'title': 'Регистрация клиента'
    })


@csrf_protect
@require_http_methods(["GET", "POST"])
def client_login(request):
    """Вход для клиента"""
    if request.method == 'POST':
        form = ClientLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            
            # Используем authenticate с нашим кастомным бэкендом
            try:
                client = Client.objects.get(email=email, is_active=True)
                if client.check_password(password):
                    # Сохраняем информацию в сессии для веб-интерфейса
                    request.session['client_id'] = client.id
                    request.session['client_email'] = client.email
                    request.session['client_name'] = f'{client.first_name} {client.last_name}'
                    messages.success(request, f'Добро пожаловать, {client.first_name}!')
                    return redirect('index')
                else:
                    messages.error(request, 'Неверный пароль')
            except Client.DoesNotExist:
                messages.error(request, 'Клиент с таким email не найден')
    else:
        form = ClientLoginForm()
    
    return render(request, 'marketplace/auth/client_login.html', {
        'form': form,
        'title': 'Вход для клиента'
    })


@csrf_protect
@require_http_methods(["GET", "POST"])
def seller_login(request):
    """Вход для продавца"""
    if request.method == 'POST':
        form = SellerLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            
            try:
                seller = Seller.objects.get(email=email, is_active=True)
                if seller.check_password(password):
                    # Сохраняем информацию в сессии для веб-интерфейса
                    request.session['seller_id'] = seller.id
                    request.session['seller_email'] = seller.email
                    request.session['seller_company'] = seller.company_name
                    messages.success(request, f'Добро пожаловать, {seller.company_name}!')
                    return redirect('index')
                else:
                    messages.error(request, 'Неверный пароль')
            except Seller.DoesNotExist:
                messages.error(request, 'Продавец с таким email не найден')
    else:
        form = SellerLoginForm()
    
    return render(request, 'marketplace/auth/seller_login.html', {
        'form': form,
        'title': 'Вход для продавца'
    })


@require_http_methods(["GET", "POST"])
def logout(request):
    """Выход из системы"""
    request.session.flush()
    messages.info(request, 'Вы вышли из системы')
    return redirect('index')
