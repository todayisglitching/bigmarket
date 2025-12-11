from django import forms
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from .models import Client, Seller, Product, Tag


class ClientRegistrationForm(forms.ModelForm):
    """Форма регистрации клиента"""
    password = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-2 rounded-lg bg-neutral-950 border border-neutral-800 focus:border-blue-400 focus:ring-1 focus:ring-blue-400 text-white placeholder:text-white/40 outline-none transition',
            'placeholder': 'Введите пароль'
        }),
        min_length=8,
        help_text='Минимум 8 символов'
    )
    password_confirm = forms.CharField(
        label='Подтверждение пароля',
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-2 rounded-lg bg-neutral-950 border border-neutral-800 focus:border-blue-400 focus:ring-1 focus:ring-blue-400 text-white placeholder:text-white/40 outline-none transition',
            'placeholder': 'Повторите пароль'
        })
    )
    
    class Meta:
        model = Client
        fields = ['email', 'first_name', 'last_name', 'phone']
        widgets = {
            'email': forms.EmailInput(attrs={
                'class': 'w-full px-4 py-2 rounded-lg bg-neutral-950 border border-neutral-800 focus:border-blue-400 focus:ring-1 focus:ring-blue-400 text-white placeholder:text-white/40 outline-none transition',
                'placeholder': 'example@email.com'
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 rounded-lg bg-neutral-950 border border-neutral-800 focus:border-blue-400 focus:ring-1 focus:ring-blue-400 text-white placeholder:text-white/40 outline-none transition',
                'placeholder': 'Имя'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 rounded-lg bg-neutral-950 border border-neutral-800 focus:border-blue-400 focus:ring-1 focus:ring-blue-400 text-white placeholder:text-white/40 outline-none transition',
                'placeholder': 'Фамилия'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 rounded-lg bg-neutral-950 border border-neutral-800 focus:border-blue-400 focus:ring-1 focus:ring-blue-400 text-white placeholder:text-white/40 outline-none transition',
                'placeholder': '+79991234567'
            }),
        }
        labels = {
            'email': 'Email',
            'first_name': 'Имя',
            'last_name': 'Фамилия',
            'phone': 'Телефон (необязательно)',
        }
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            email = email.lower().strip()
            if Client.objects.filter(email=email).exists():
                raise ValidationError('Клиент с таким email уже существует')
            if Seller.objects.filter(email=email).exists():
                raise ValidationError('Этот email уже используется')
        return email
    
    def clean_password(self):
        password = self.cleaned_data.get('password')
        if password:
            try:
                validate_password(password)
            except ValidationError as e:
                raise ValidationError(e.messages)
        return password
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')
        
        if password and password_confirm:
            if password != password_confirm:
                raise ValidationError({
                    'password_confirm': 'Пароли не совпадают'
                })
        
        return cleaned_data
    
    def save(self, commit=True):
        client = super().save(commit=False)
        password = self.cleaned_data.get('password')
        if password:
            client.set_password(password)  # Пароль автоматически хешируется
        if commit:
            client.save()
        return client


class ClientLoginForm(forms.Form):
    """Форма входа для клиента"""
    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={
            'class': 'w-full px-4 py-2 rounded-lg bg-neutral-950 border border-neutral-800 focus:border-blue-400 focus:ring-1 focus:ring-blue-400 text-white placeholder:text-white/40 outline-none transition',
            'placeholder': 'example@email.com'
        })
    )
    password = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-2 rounded-lg bg-neutral-950 border border-neutral-800 focus:border-blue-400 focus:ring-1 focus:ring-blue-400 text-white placeholder:text-white/40 outline-none transition',
            'placeholder': 'Введите пароль'
        })
    )
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            return email.lower().strip()
        return email


class SellerLoginForm(forms.Form):
    """Форма входа для продавца"""
    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={
            'class': 'w-full px-4 py-2 rounded-lg bg-neutral-950 border border-neutral-800 focus:border-blue-400 focus:ring-1 focus:ring-blue-400 text-white placeholder:text-white/40 outline-none transition',
            'placeholder': 'seller@company.com'
        })
    )
    password = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-2 rounded-lg bg-neutral-950 border border-neutral-800 focus:border-blue-400 focus:ring-1 focus:ring-blue-400 text-white placeholder:text-white/40 outline-none transition',
            'placeholder': 'Введите пароль'
        })
    )
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            return email.lower().strip()
        return email


class ProductForm(forms.ModelForm):
    """Форма для создания и редактирования продукта продавцом"""
    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'space-y-2'
        }),
        label='Теги'
    )
    
    class Meta:
        model = Product
        fields = ['title', 'description', 'thumbnail', 'price', 'stock', 'tags']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 rounded-lg bg-neutral-950 border border-neutral-800 focus:border-blue-400 focus:ring-1 focus:ring-blue-400 text-white placeholder:text-white/40 outline-none transition',
                'placeholder': 'Название продукта'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 rounded-lg bg-neutral-950 border border-neutral-800 focus:border-blue-400 focus:ring-1 focus:ring-blue-400 text-white placeholder:text-white/40 outline-none transition',
                'placeholder': 'Подробное описание продукта',
                'rows': 5
            }),
            'thumbnail': forms.FileInput(attrs={
                'class': 'w-full px-4 py-2 rounded-lg bg-neutral-950 border border-neutral-800 focus:border-blue-400 focus:ring-1 focus:ring-blue-400 text-white outline-none transition',
                'accept': 'image/*'
            }),
            'price': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 rounded-lg bg-neutral-950 border border-neutral-800 focus:border-blue-400 focus:ring-1 focus:ring-blue-400 text-white placeholder:text-white/40 outline-none transition',
                'placeholder': '0.00',
                'step': '0.01',
                'min': '0'
            }),
            'stock': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 rounded-lg bg-neutral-950 border border-neutral-800 focus:border-blue-400 focus:ring-1 focus:ring-blue-400 text-white placeholder:text-white/40 outline-none transition',
                'placeholder': '0',
                'min': '0'
            }),
        }
        labels = {
            'title': 'Название',
            'description': 'Описание',
            'thumbnail': 'Миниатюра',
            'price': 'Цена (₽)',
            'stock': 'Остаток на складе',
        }
    
    def clean_title(self):
        title = self.cleaned_data.get('title')
        if title and len(title.strip()) < 3:
            raise ValidationError('Название должно содержать минимум 3 символа')
        return title.strip()
    
    def clean_description(self):
        description = self.cleaned_data.get('description')
        if description and len(description.strip()) < 10:
            raise ValidationError('Описание должно содержать минимум 10 символов')
        return description.strip()
    
    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price is not None and price < 0:
            raise ValidationError('Цена не может быть отрицательной')
        return price
    
    def clean_stock(self):
        stock = self.cleaned_data.get('stock')
        if stock is not None and stock < 0:
            raise ValidationError('Остаток не может быть отрицательным')
        return stock
