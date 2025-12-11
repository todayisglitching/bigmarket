# Документация по моделям

## Модель Product (Продукт)

### Описание
Модель для хранения информации о продуктах в маркетплейсе.

### Поля

#### Основная информация
- **id** (BigAutoField) - уникальный идентификатор продукта (автоматически)
- **title** (CharField, max_length=255) - название продукта
  - Обязательное поле
  - Минимум 3 символа
  - Валидация: MinLengthValidator(3)
  
- **description** (TextField) - подробное описание продукта
  - Обязательное поле
  - Минимум 10 символов
  - Валидация: MinLengthValidator(10)

#### Цена и наличие
- **price** (DecimalField) - цена продукта в рублях
  - Тип: DecimalField(max_digits=10, decimal_places=2)
  - По умолчанию: 0.00
  - Обязательное поле
  - Валидация: MinValueValidator(0) - цена не может быть отрицательной
  
- **stock** (PositiveIntegerField) - количество товара на складе
  - По умолчанию: 0
  - Обязательное поле
  - Автоматически проверяет, что значение >= 0

#### Медиа
- **thumbnail** (ImageField) - миниатюра продукта
  - Опциональное поле
  - Загружается в: `products/thumbnails/`
  
- **photos** (JSONField) - массив URL фотографий
  - По умолчанию: пустой список []
  - Максимум 10 фотографий
  - Формат: список строк с URL

#### Связи
- **seller** (ForeignKey) - продавец, который создал продукт
  - Связь с моделью Seller
  - Обязательное поле
  - При удалении продавца удаляются все его продукты (CASCADE)
  - related_name: 'products'
  
- **tags** (ManyToManyField) - теги продукта
  - Связь с моделью Tag
  - Опциональное поле
  - related_name: 'products'

#### Статус и даты
- **checked** (BooleanField) - проверен ли продукт администратором
  - По умолчанию: False
  - Может быть изменено только администратором через админ-панель
  - Продукты с checked=False не видны клиентам
  
- **created_at** (DateTimeField) - дата создания продукта
  - Автоматически устанавливается при создании
  - Только для чтения
  
- **updated_at** (DateTimeField) - дата последнего обновления
  - Автоматически обновляется при каждом сохранении
  - Только для чтения

### Индексы
- Индекс по полю `created_at` (по убыванию) для быстрой сортировки
- Индекс по полю `checked` для быстрой фильтрации

### Методы
- `__str__()` - возвращает название продукта

### Пример использования
```python
from marketplace.models import Product, Seller, Tag

# Создание продукта
seller = Seller.objects.get(email='seller@example.com')
product = Product.objects.create(
    title='Новый продукт',
    description='Описание нового продукта',
    price=1999.99,
    stock=50,
    seller=seller
)

# Добавление тегов
tag1 = Tag.objects.get(tagtitle='Электроника')
tag2 = Tag.objects.create(tagtitle='Смартфоны')
product.tags.add(tag1, tag2)

# Получение продуктов продавца
seller_products = seller.products.all()

# Получение только проверенных продуктов
checked_products = Product.objects.filter(checked=True)
```

---

## Модель Tag (Тег)

### Описание
Модель для хранения тегов, которые можно присваивать продуктам.

### Поля
- **id** (BigAutoField) - уникальный идентификатор тега (автоматически)
- **tagtitle** (CharField, max_length=100) - название тега
  - Обязательное поле
  - Уникальное значение
  - Минимум 2 символа
  - Валидация: MinLengthValidator(2)
  
- **created_at** (DateTimeField) - дата создания тега
  - Автоматически устанавливается при создании
  - Только для чтения

### Связи
- **products** (ManyToManyField через Product) - продукты с этим тегом
  - Обратная связь от модели Product
  - related_name: 'products'

### Сортировка
- По умолчанию сортируется по `tagtitle` (алфавитный порядок)

### Методы
- `__str__()` - возвращает название тега

### Пример использования
```python
from marketplace.models import Tag

# Создание тега
tag = Tag.objects.create(tagtitle='Электроника')

# Получение всех продуктов с этим тегом
products_with_tag = tag.products.all()
```

---

## Модель Seller (Продавец)

### Описание
Модель для хранения информации о продавцах. Наследуется от AbstractBaseUser и PermissionsMixin для поддержки аутентификации.

### Поля

#### Основная информация
- **id** (BigAutoField) - уникальный идентификатор (автоматически)
- **email** (EmailField) - email адрес
  - Обязательное поле
  - Уникальное значение
  - Используется как USERNAME_FIELD для входа
  
- **company_name** (CharField, max_length=255) - название компании
  - Обязательное поле
  - REQUIRED_FIELDS
  
- **contact_person** (CharField, max_length=255) - контактное лицо
  - Обязательное поле
  - REQUIRED_FIELDS
  
- **phone** (CharField, max_length=20) - телефон
  - Обязательное поле

#### Безопасность
- **token** (CharField, max_length=64) - токен для API аутентификации
  - Уникальное значение
  - Генерируется автоматически при создании
  - Только для чтения
  - Используется для доступа к API
  
- **password** (CharField) - зашифрованный пароль
  - Хранится в зашифрованном виде (PBKDF2)
  - Никогда не хранится в открытом виде
  - Устанавливается через `set_password()`
  - Проверяется через `check_password()`

#### Статус
- **is_active** (BooleanField) - активен ли аккаунт
  - По умолчанию: True
  - Неактивные продавцы не могут войти в систему
  
- **is_staff** (BooleanField) - является ли персоналом
  - По умолчанию: False
  - Дает доступ к админ-панели
  
- **is_superuser** (BooleanField) - является ли суперпользователем
  - По умолчанию: False
  - Дает полный доступ ко всем функциям

#### Даты
- **date_joined** (DateTimeField) - дата регистрации
  - Автоматически устанавливается при создании
  - Только для чтения
  
- **last_login** (DateTimeField) - дата последнего входа
  - Автоматически обновляется при входе
  - Только для чтения

#### Права доступа (через PermissionsMixin)
- **groups** (ManyToManyField) - группы пользователей
  - related_name: 'seller_set'
  
- **user_permissions** (ManyToManyField) - права доступа
  - related_name: 'seller_set'

### Связи
- **products** (ForeignKey через Product) - продукты продавца
  - Обратная связь от модели Product
  - related_name: 'products'

### Методы
- `__str__()` - возвращает "Название компании (email)"
- `regenerate_token()` - регенерирует токен продавца
- `set_password(raw_password)` - устанавливает зашифрованный пароль
- `check_password(raw_password)` - проверяет пароль

### Менеджер
- `objects` - UserManager для создания пользователей
  - `create_user(email, password, **extra_fields)` - создание обычного пользователя
  - `create_superuser(email, password, **extra_fields)` - создание суперпользователя

### Пример использования
```python
from marketplace.models import Seller

# Создание продавца
seller = Seller.objects.create_user(
    email='seller@example.com',
    password='secure_password',
    company_name='ООО Товары',
    contact_person='Иван Иванов',
    phone='+79991234567'
)

# Получение токена
token = seller.token

# Проверка пароля
if seller.check_password('secure_password'):
    print('Пароль верный')

# Регенерация токена
seller.regenerate_token()

# Получение всех продуктов продавца
products = seller.products.all()
```

---

## Модель Client (Клиент)

### Описание
Модель для хранения информации о клиентах (покупателях). Наследуется от AbstractBaseUser и PermissionsMixin для поддержки аутентификации.

### Поля

#### Основная информация
- **id** (BigAutoField) - уникальный идентификатор (автоматически)
- **email** (EmailField) - email адрес
  - Обязательное поле
  - Уникальное значение
  - Используется как USERNAME_FIELD для входа
  
- **first_name** (CharField, max_length=150) - имя
  - Обязательное поле
  - REQUIRED_FIELDS
  
- **last_name** (CharField, max_length=150) - фамилия
  - Обязательное поле
  - REQUIRED_FIELDS
  
- **phone** (CharField, max_length=20) - телефон
  - Опциональное поле

#### Безопасность
- **token** (CharField, max_length=64) - токен для API аутентификации
  - Уникальное значение
  - Генерируется автоматически при создании
  - Только для чтения
  - Используется для доступа к API
  
- **password** (CharField) - зашифрованный пароль
  - Хранится в зашифрованном виде (PBKDF2)
  - Никогда не хранится в открытом виде
  - Устанавливается через `set_password()`
  - Проверяется через `check_password()`

#### Статус
- **is_active** (BooleanField) - активен ли аккаунт
  - По умолчанию: True
  - Неактивные клиенты не могут войти в систему
  
- **is_staff** (BooleanField) - является ли персоналом
  - По умолчанию: False
  - Дает доступ к админ-панели
  
- **is_superuser** (BooleanField) - является ли суперпользователем
  - По умолчанию: False
  - Дает полный доступ ко всем функциям

#### Даты
- **date_joined** (DateTimeField) - дата регистрации
  - Автоматически устанавливается при создании
  - Только для чтения
  
- **last_login** (DateTimeField) - дата последнего входа
  - Автоматически обновляется при входе
  - Только для чтения

#### Права доступа (через PermissionsMixin)
- **groups** (ManyToManyField) - группы пользователей
  - related_name: 'client_set'
  
- **user_permissions** (ManyToManyField) - права доступа
  - related_name: 'client_set'

### Методы
- `__str__()` - возвращает "Имя Фамилия (email)"
- `regenerate_token()` - регенерирует токен клиента
- `set_password(raw_password)` - устанавливает зашифрованный пароль
- `check_password(raw_password)` - проверяет пароль

### Менеджер
- `objects` - UserManager для создания пользователей
  - `create_user(email, password, **extra_fields)` - создание обычного пользователя
  - `create_superuser(email, password, **extra_fields)` - создание суперпользователя

### Пример использования
```python
from marketplace.models import Client

# Создание клиента
client = Client.objects.create_user(
    email='client@example.com',
    password='secure_password',
    first_name='Петр',
    last_name='Петров',
    phone='+79991234568'
)

# Получение токена
token = client.token

# Проверка пароля
if client.check_password('secure_password'):
    print('Пароль верный')

# Регенерация токена
client.regenerate_token()
```

---

## Связи между моделями

```
Seller (1) ────< (N) Product
                    │
                    │ (N)
                    │
                    ▼
                  Tag (N)
```

- Один продавец может иметь много продуктов
- Один продукт принадлежит одному продавцу
- Один продукт может иметь много тегов
- Один тег может быть присвоен многим продуктам

## Безопасность

### Хеширование паролей
- Все пароли хранятся в зашифрованном виде
- Используется алгоритм PBKDF2 (по умолчанию в Django)
- Пароли никогда не хранятся в открытом виде
- Хеш включает соль для дополнительной безопасности

### Токены
- Токены генерируются автоматически при создании пользователя
- Используется `secrets.token_urlsafe(32)` для генерации безопасных токенов
- Токены уникальны для каждого пользователя
- Можно регенерировать через метод `regenerate_token()`

### Валидация
- Все поля проходят валидацию перед сохранением
- Email проверяется на уникальность
- Пароли проверяются через Django password validators
- Цены и остатки не могут быть отрицательными
