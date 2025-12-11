# API Документация

## Безопасность

Все API эндпоинты используют токен-аутентификацию. Токен передается в заголовке:
```
Authorization: Token <your_token>
```

## Регистрация

### Регистрация продавца
**POST** `/api/auth/seller/register/`

Тело запроса:
```json
{
    "email": "seller@example.com",
    "password": "secure_password123",
    "password_confirm": "secure_password123",
    "company_name": "ООО Товары",
    "contact_person": "Иван Иванов",
    "phone": "+79991234567"
}
```

Ответ:
```json
{
    "message": "Продавец успешно зарегистрирован",
    "token": "your_token_here",
    "seller": {
        "id": 1,
        "email": "seller@example.com",
        "company_name": "ООО Товары",
        "contact_person": "Иван Иванов",
        "phone": "+79991234567",
        "date_joined": "2024-01-01T12:00:00Z"
    }
}
```

### Регистрация клиента
**POST** `/api/auth/client/register/`

Тело запроса:
```json
{
    "email": "client@example.com",
    "password": "secure_password123",
    "password_confirm": "secure_password123",
    "first_name": "Петр",
    "last_name": "Петров",
    "phone": "+79991234568"
}
```

Ответ:
```json
{
    "message": "Клиент успешно зарегистрирован",
    "token": "your_token_here",
    "client": {
        "id": 1,
        "email": "client@example.com",
        "first_name": "Петр",
        "last_name": "Петров",
        "phone": "+79991234568",
        "date_joined": "2024-01-01T12:00:00Z"
    }
}
```

## Продукты

### Получить список продуктов
**GET** `/api/products/`

- Неавторизованные пользователи видят только проверенные продукты (`checked=True`)
- Клиенты видят только проверенные продукты
- Продавцы видят свои продукты + все проверенные
- Администраторы видят все продукты

Параметры запроса:
- `page` - номер страницы (пагинация)
- `search` - поиск по названию (если реализовано)

### Получить детали продукта
**GET** `/api/products/{id}/`

### Создать продукт (только для продавцов)
**POST** `/api/products/`

Заголовки:
```
Authorization: Token <seller_token>
Content-Type: multipart/form-data
```

Тело запроса:
```json
{
    "title": "Название продукта",
    "description": "Подробное описание продукта",
    "thumbnail": <file>,
    "photos": ["url1", "url2"],
    "price": 1999.99,
    "stock": 50,
    "tag_ids": [1, 2, 3]
}
```

**Поля:**
- `title` (обязательно) - название продукта, минимум 3 символа
- `description` (обязательно) - описание продукта, минимум 10 символов
- `thumbnail` (опционально) - файл миниатюры
- `photos` (опционально) - массив URL фотографий (максимум 10)
- `price` (обязательно) - цена в рублях (Decimal, минимум 0)
- `stock` (обязательно) - количество товара на складе (Integer, минимум 0)
- `tag_ids` (опционально) - массив ID тегов

**Важно:** При создании продукта `checked` автоматически устанавливается в `false`. Только администратор может изменить это поле через админ-панель Django.

### Обновить продукт (только владелец)
**PUT/PATCH** `/api/products/{id}/`

Заголовки:
```
Authorization: Token <seller_token>
```

**Важно:** Поле `checked` нельзя изменить через API, даже если оно передано в запросе.

### Удалить продукт (только владелец)
**DELETE** `/api/products/{id}/`

### Получить мои продукты (только для продавцов)
**GET** `/api/products/my_products/`

Заголовки:
```
Authorization: Token <seller_token>
```

### Получить похожие продукты
**GET** `/api/products/{id}/similar/`

## Теги

### Получить список тегов
**GET** `/api/tags/`

### Получить детали тега
**GET** `/api/tags/{id}/`

## Профили

### Получить профиль продавца
**GET** `/api/auth/seller/profile/`

Заголовки:
```
Authorization: Token <seller_token>
```

### Обновить профиль продавца
**PATCH** `/api/auth/seller/profile/`

### Получить профиль клиента
**GET** `/api/auth/client/profile/`

Заголовки:
```
Authorization: Token <client_token>
```

### Обновить профиль клиента
**PATCH** `/api/auth/client/profile/`

## Примеры использования

### Python (requests)
```python
import requests

# Регистрация продавца
response = requests.post('http://localhost:8000/api/auth/seller/register/', json={
    'email': 'seller@example.com',
    'password': 'password123',
    'password_confirm': 'password123',
    'company_name': 'ООО Товары',
    'contact_person': 'Иван Иванов',
    'phone': '+79991234567'
})
token = response.json()['token']

# Создание продукта
headers = {'Authorization': f'Token {token}'}
response = requests.post('http://localhost:8000/api/products/', 
    headers=headers,
    json={
        'title': 'Новый продукт',
        'description': 'Описание продукта',
        'price': 1999.99,
        'stock': 50,
        'photos': [],
        'tag_ids': []
    }
)
```

### cURL
```bash
# Регистрация
curl -X POST http://localhost:8000/api/auth/seller/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "seller@example.com",
    "password": "password123",
    "password_confirm": "password123",
    "company_name": "ООО Товары",
    "contact_person": "Иван Иванов",
    "phone": "+79991234567"
  }'

# Создание продукта
curl -X POST http://localhost:8000/api/products/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Новый продукт",
    "description": "Описание",
    "price": 1999.99,
    "stock": 50,
    "photos": [],
    "tag_ids": []
  }'
```

## Безопасность

1. **Токены** генерируются автоматически при регистрации и хранятся в базе данных
2. **Пароли** хешируются с использованием Django's password hashing
3. **Валидация** всех входных данных на уровне сериализаторов
4. **Права доступа** проверяются на каждом эндпоинте
5. **CSRF защита** включена для веб-интерфейса
6. **Поле checked** может быть изменено только администратором через админ-панель

## Ошибки

API возвращает стандартные HTTP коды статуса:
- `200` - Успешно
- `201` - Создано
- `400` - Ошибка валидации
- `401` - Не авторизован
- `403` - Доступ запрещен
- `404` - Не найдено
- `500` - Ошибка сервера

Пример ошибки:
```json
{
    "detail": "Неверный токен или пользователь неактивен"
}
```
