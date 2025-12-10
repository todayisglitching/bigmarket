from django.shortcuts import render


CATEGORIES = [
    {
        "code": "tech",
        "title": "Электроника",
        "subtitle": "Для работы, учебы и развлечений",
        "count": 48,
    },
    {
        "code": "home",
        "title": "Дом и уют",
        "subtitle": "Текстиль, декор и освещение",
        "count": 32,
    },
    {
        "code": "sport",
        "title": "Спорт и активность",
        "subtitle": "Экипировка и гаджеты",
        "count": 27,
    },
]

PRODUCTS = [
    {
        "id": 1,
        "title": "Беспроводные наушники AirWave",
        "category": "Электроника",
        "description": "Легкие наушники с шумоподавлением и автономностью до 24 часов.",
        "price": 4990,
        "stock": 12,
        "features": [
            {"name": "Тип подключения", "value": "Bluetooth 5.3"},
            {"name": "Шумоподавление", "value": "ANC, 2 микрофона"},
            {"name": "Работа от батареи", "value": "до 24 часов"},
        ],
    },
    {
        "id": 2,
        "title": "Умная лампа Luma",
        "category": "Дом и уют",
        "description": "Настраиваемая температура света, управление с телефона и голосом.",
        "price": 1290,
        "stock": 30,
        "features": [
            {"name": "Цветовая температура", "value": "2700–6500K"},
            {"name": "Управление", "value": "Мобильное приложение"},
            {"name": "Совместимость", "value": "Google / Alexa / HomeKit"},
        ],
    },
    {
        "id": 3,
        "title": "Фитнес-браслет Pulse Pro",
        "category": "Спорт и активность",
        "description": "Отслеживание пульса, сна и тренировок, водозащита до 5 ATM.",
        "price": 3490,
        "stock": 18,
        "features": [
            {"name": "Датчики", "value": "Пульс, SpO₂, шаги"},
            {"name": "Экран", "value": "AMOLED 1.1”"},
            {"name": "Автономность", "value": "до 10 дней"},
        ],
    },
]


def index(request):
    return render(
        request,
        "marketplace/home.html",
        {
            "categories": CATEGORIES,
            "products": PRODUCTS,
        },
    )


def product_detail(request, product_id: int):
    product = next((p for p in PRODUCTS if p["id"] == product_id), PRODUCTS[0])
    similar = [p for p in PRODUCTS if p["id"] != product["id"]][:3]
    return render(
        request,
        "marketplace/product_detail.html",
        {
            "product": product,
            "similar": similar,
        },
    )
