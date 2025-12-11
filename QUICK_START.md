# Быстрый старт

## 1. Установка (5 минут)

```bash
# Установить зависимости
pip install -r requirements.txt

# Обновить settings.py (см. SETTINGS_UPDATE.md)
# Добавить 'rest_framework' в INSTALLED_APPS
# Добавить настройки REST_FRAMEWORK
# Добавить MEDIA_URL и MEDIA_ROOT

# Создать миграции
python manage.py makemigrations marketplace

# Применить миграции
python manage.py migrate

# Создать суперпользователя
python manage.py createsuperuser

# Запустить сервер
python manage.py runserver
```

## 2. Тестирование регистрации

### Регистрация продавца:
```bash
curl -X POST http://localhost:8000/api/auth/seller/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "seller@test.com",
    "password": "testpass123",
    "password_confirm": "testpass123",
    "company_name": "Тестовая компания",
    "contact_person": "Иван Иванов",
    "phone": "+79991234567"
  }'
```

Сохраните полученный `token`!

### Создание продукта:
```bash
curl -X POST http://localhost:8000/api/products/ \
  -H "Authorization: Token YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Тестовый продукт",
    "description": "Описание тестового продукта для проверки",
    "photos": [],
    "tag_ids": []
  }'
```

## 3. Админ-панель

Откройте: http://localhost:8000/admin/

Здесь вы можете:
- Увидеть созданный продукт с `checked=False`
- Изменить `checked` на `True` (только администратор!)
- Управлять тегами, продавцами, клиентами

## 4. Проверка работы

После того как вы установите `checked=True` в админке:
- Продукт появится в списке: `GET /api/products/`
- Продукт будет виден на главной странице: http://localhost:8000/

## Важно!

- Продукты создаются с `checked=False`
- Только администратор может изменить `checked` через админку
- Клиенты видят только продукты с `checked=True`
- Продавцы видят свои продукты + все проверенные
