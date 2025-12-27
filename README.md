# 🛒 MyShop — интернет-магазин (Django + DRF + JWT + Docker)

Полнофункциональный бэкенд интернет-магазина с авторизацией через JWT, корзиной, заказами, фильтрацией, документацией Swagger и полноценным API-слоем.

---

## 📌 Описание

Проект реализован на базе:

- **Django 5**
- **Django REST Framework**
- **SimpleJWT** (access/refresh токены)
- **drf-spectacular** (Swagger / OpenAPI)
- **SQLite / PostgreSQL**
- **Docker + Docker Compose**
- **pytest + pytest-django + coverage**

Включает в себя:

- регистрацию и авторизацию через JWT
- управление корзиной
- оформление заказов
- CRUD товаров и отзывов
- админ-панель
- API-документацию Swagger (`/swagger/`)
- автогенерацию схемы OpenAPI (`/api/schema/`)

---

## 🚀 Установка и запуск через Docker

Убедись, что у тебя установлены:

- Docker
- Docker Compose

### 1️⃣ Клонировать проект

```bash
git clone https://github.com/stdimka/myshop.git
cd myshop

2️⃣ Собрать контейнеры
docker-compose build

3️⃣ Запустить
docker-compose up -d

4️⃣ Применить миграции (внутри контейнера)
docker-compose exec web python manage.py migrate

5️⃣ Создать суперпользователя (опционально)
docker-compose exec web python manage.py createsuperuser


После запуска API доступно по адресу:
http://127.0.0.1:8000/


🔐 JWT авторизация + API примеры

DRF SimpleJWT предоставляет два ключевых эндпоинта:

▶ Получение токенов
POST /api/token/

Body:
{
  "username": "root",
  "password": "123"
}

Ответ:
{
  "access": "eyJhbGciOi...",
  "refresh": "eyJhbGciOi..."
}

▶ Обновление токена
POST /api/token/refresh/

Body:
{
  "refresh": "eyJhbGc..."
}


▶ Использование access-токена в запросах
curl -X GET http://127.0.0.1:8000/api/products/ \
  -H "Authorization: Bearer <ACCESS_TOKEN>"


📘 Документация API

Swagger UI:
http://127.0.0.1:8000/swagger/

Redoc:
http://127.0.0.1:8000/api/redoc/

JSON-схема OpenAPI:
http://127.0.0.1:8000/api/schema/


🧪 Запуск тестов и линтеров
▶ Запуск pytest
pytest -v

С покрытием:
pytest --cov=.

▶ Линтер flake8
flake8 .


myshop/
├── __pycache__/
│   └── conftest.cpython-313-pytest-8.4.2.pyc
├── adminapp/
│   ├── __pycache__/
│   │   ├── __init__.cpython-312.pyc
│   │   ├── __init__.cpython-313.pyc
│   │   ├── admin.cpython-312.pyc
│   │   ├── admin.cpython-313.pyc
│   │   ├── apps.cpython-312.pyc
│   │   ├── apps.cpython-313.pyc
│   │   ├── models.cpython-312.pyc
│   │   ├── models.cpython-313.pyc
│   │   ├── tests.cpython-313-pytest-8.4.2.pyc
│   │   ├── urls.cpython-312.pyc
│   │   ├── urls.cpython-313.pyc
│   │   ├── views.cpython-312.pyc
│   │   └── views.cpython-313.pyc
│   ├── migrations/
│   │   ├── __pycache__/
│   │   │   ├── __init__.cpython-312.pyc
│   │   │   └── __init__.cpython-313.pyc
│   │   └── __init__.py
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
├── main/
│   ├── __pycache__/
│   │   ├── __init__.cpython-312.pyc
│   │   ├── __init__.cpython-313.pyc
│   │   ├── local_settings.cpython-312.pyc
│   │   ├── local_settings.cpython-313.pyc
│   │   ├── settings.cpython-312.pyc
│   │   ├── settings.cpython-313.pyc
│   │   ├── urls.cpython-312.pyc
│   │   ├── urls.cpython-313.pyc
│   │   ├── wsgi.cpython-312.pyc
│   │   └── wsgi.cpython-313.pyc
│   ├── __init__.py
│   ├── asgi.py
│   ├── local_settings.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── media/
│   ├── products/
│       ├── caramel_malt.jpg
│       ├── cascade_hops.jpg
│       ├── centennial_hops.jpg
│       ├── citra_hops.jpg
│       ├── imperial_yeast.jpg
│       ├── ipa_kit.jpg
│       ├── maris_otter_malt.jpg
│       ├── mosaic_hops.jpg
│       ├── pilsner_malt.jpg
│       ├── saaz_hops.jpg
│       ├── safale_us05_yeast.jpg
│       └── unmalted_wheat.jpg
├── shop/
│   ├── __pycache__/
│   │   ├── __init__.cpython-312.pyc
│   │   ├── __init__.cpython-313.pyc
│   │   ├── admin.cpython-312.pyc
│   │   ├── admin.cpython-313.pyc
│   │   ├── apps.cpython-312.pyc
│   │   ├── apps.cpython-313.pyc
│   │   ├── models.cpython-312.pyc
│   │   ├── models.cpython-313.pyc
│   │   ├── urls.cpython-312.pyc
│   │   ├── urls.cpython-313.pyc
│   │   ├── views.cpython-312.pyc
│   │   └── views.cpython-313.pyc
│   ├── api/
│   │   ├── __pycache__/
│   │   │   ├── __init__.cpython-312.pyc
│   │   │   ├── __init__.cpython-313.pyc
│   │   │   ├── serializers.cpython-312.pyc
│   │   │   ├── serializers.cpython-313.pyc
│   │   │   ├── urls.cpython-312.pyc
│   │   │   ├── urls.cpython-313.pyc
│   │   │   ├── views.cpython-312.pyc
│   │   │   └── views.cpython-313.pyc
│   │   ├── __init__.py
│   │   ├── serializers.py
│   │   ├── urls.py
│   │   └── views.py
│   ├── migrations/
│   │   ├── __pycache__/
│   │   │   ├── 0001_initial.cpython-312.pyc
│   │   │   ├── 0001_initial.cpython-313.pyc
│   │   │   ├── 0002_remove_product_category_id_category_product_category.cpython-312.pyc
│   │   │   ├── 0002_remove_product_category_id_category_product_category.cpython-313.pyc
│   │   │   ├── 0003_alter_product_category.cpython-312.pyc
│   │   │   ├── 0003_alter_product_category.cpython-313.pyc
│   │   │   ├── 0004_alter_order_total_price_alter_orderitem_price_and_more.cpython-312.pyc
│   │   │   ├── 0004_alter_order_total_price_alter_orderitem_price_and_more.cpython-313.pyc
│   │   │   ├── 0005_cart_cartitem.cpython-312.pyc
│   │   │   ├── 0005_cart_cartitem.cpython-313.pyc
│   │   │   ├── __init__.cpython-312.pyc
│   │   │   └── __init__.cpython-313.pyc
│   │   ├── 0001_initial.py
│   │   ├── 0002_remove_product_category_id_category_product_category.py
│   │   ├── 0003_alter_product_category.py
│   │   ├── 0004_alter_order_total_price_alter_orderitem_price_and_more.py
│   │   ├── 0005_cart_cartitem.py
│   │   └── __init__.py
│   ├── tests/
│   │   ├── __pycache__/
│   │   │   ├── test_additional.cpython-313-pytest-8.4.2.pyc
│   │   │   ├── test_api_safe.cpython-313-pytest-8.4.2.pyc
│   │   │   ├── test_extra_safe.cpython-313-pytest-8.4.2.pyc
│   │   │   ├── test_order.cpython-313-pytest-8.4.2.pyc
│   │   │   ├── test_payment.cpython-313-pytest-8.4.2.pyc
│   │   │   ├── test_product.cpython-313-pytest-8.4.2.pyc
│   │   │   ├── test_review.cpython-313-pytest-8.4.2.pyc
│   │   │   ├── test_safe_generated.cpython-313-pytest-8.4.2.pyc
│   │   │   └── test_signals_and_jobs.cpython-313-pytest-8.4.2.pyc
│   │   ├── test_api_safe.py
│   │   ├── test_extra_safe.py
│   │   ├── test_order.py
│   │   ├── test_payment.py
│   │   ├── test_product.py
│   │   ├── test_review.py
│   │   ├── test_safe_generated.py
│   │   └── test_signals_and_jobs.py
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── urls.py
│   └── views.py
├── static/
│   ├── css/
│   │   └── main.css
│   ├── img/
│   │   ├── avatars/
│   │   │   ├── avatar1.svg
│   │   │   ├── avatar10.svg
│   │   │   ├── avatar2.svg
│   │   │   ├── avatar3.svg
│   │   │   ├── avatar4.svg
│   │   │   ├── avatar5.svg
│   │   │   ├── avatar6.svg
│   │   │   ├── avatar7.svg
│   │   │   ├── avatar8.svg
│   │   │   └── avatar9.svg
│   │   ├── background/
│   │   │   ├── hopfen-fields.jpg
│   │   │   ├── image-footer.svg
│   │   │   └── pattern.jpg
│   │   ├── icons/
│   │   │   ├── Shopping_bag.svg
│   │   │   └── User_alt.svg
│   │   ├── products/
│   │   │   ├── caramel_malt.jpg
│   │   │   ├── cascade_hops.jpg
│   │   │   ├── centennial_hops.jpg
│   │   │   ├── citra_hops.jpg
│   │   │   ├── imperial_yeast.jpg
│   │   │   ├── ipa_kit.jpg
│   │   │   ├── maris_otter_malt.jpg
│   │   │   ├── mosaic_hops.jpg
│   │   │   ├── pilsner_malt.jpg
│   │   │   ├── saaz_hops.jpg
│   │   │   ├── safale_us05_yeast.jpg
│   │   │   └── unmalted_wheat.jpg
│   │   └── logo.svg
│   ├── js/
│       └── main.js
├── templates/
│   ├── account/
│   │   └── account.html
│   ├── admin/
│   │   ├── add.html
│   │   ├── dashboard.html
│   │   ├── permissions.html
│   │   ├── products.html
│   │   ├── search.html
│   │   └── stats.html
│   ├── auth/
│   │   ├── login.html
│   │   ├── password_reset_confirm.html
│   │   ├── password_reset_form.html
│   │   └── register.html
│   ├── products/
│   │   ├── product-caramel-malt.html
│   │   ├── product-cascade-hops.html
│   │   ├── product-centennial-hops.html
│   │   ├── product-citra-hops.html
│   │   ├── product-imperial-yeast.html
│   │   ├── product-maris-otter-malt.html
│   │   ├── product-mosaic-hops.html
│   │   ├── product-pilsner-malt.html
│   │   ├── product-saaz-hops.html
│   │   ├── product-safale-us05-yeast.html
│   │   ├── product-unmalted-wheat.html
│   │   └── product-west-coast-ipa-kit.html
│   ├── review/
│   │   └── add-update-delete-review.html
│   ├── shop/
│   │   ├── cart.html
│   │   ├── checkout.html
│   │   └── order_history.html
│   ├── base.html
│   ├── community.html
│   ├── contact.html
│   ├── faq.html
│   ├── forgot_password.html
│   ├── guides-recipes.html
│   ├── home.html
│   ├── license.html
│   └── product_detail.html
├── tests/
│   ├── __pycache__/
│   │   ├── test_email.cpython-313-pytest-8.4.2.pyc
│   │   └── test_urls_resolve.cpython-313-pytest-8.4.2.pyc
│   ├── data/
│   │   ├── __pycache__/
│   │   │   ├── urls_admin_data.cpython-313.pyc
│   │   │   ├── urls_shop_data.cpython-313.pyc
│   │   │   └── urls_user_data.cpython-313.pyc
│   │   ├── urls_admin_data.py
│   │   ├── urls_shop_data.py
│   │   └── urls_user_data.py
│   ├── test_email.py
│   └── test_urls_resolve.py
├── user/
│   ├── __pycache__/
│   │   ├── __init__.cpython-312.pyc
│   │   ├── __init__.cpython-313.pyc
│   │   ├── admin.cpython-312.pyc
│   │   ├── admin.cpython-313.pyc
│   │   ├── apps.cpython-312.pyc
│   │   ├── apps.cpython-313.pyc
│   │   ├── forms.cpython-312.pyc
│   │   ├── forms.cpython-313.pyc
│   │   ├── models.cpython-312.pyc
│   │   ├── models.cpython-313.pyc
│   │   ├── utils.cpython-312.pyc
│   │   └── utils.cpython-313.pyc
│   ├── migrations/
│   │   ├── __pycache__/
│   │   │   ├── 0001_initial.cpython-312.pyc
│   │   │   ├── 0001_initial.cpython-313.pyc
│   │   │   ├── __init__.cpython-312.pyc
│   │   │   └── __init__.cpython-313.pyc
│   │   ├── 0001_initial.py
│   │   └── __init__.py
│   ├── tests/
│   │   ├── __pycache__/
│   │   │   ├── test_forms.cpython-313-pytest-8.4.2.pyc
│   │   │   ├── test_user_profile.cpython-313-pytest-8.4.2.pyc
│   │   │   ├── test_user_token.cpython-313-pytest-8.4.2.pyc
│   │   │   └── test_views_auth.cpython-313-pytest-8.4.2.pyc
│   │   ├── test_forms.py
│   │   ├── test_user_profile.py
│   │   ├── test_user_token.py
│   │   └── test_views_auth.py
│   ├── urls/
│   │   ├── __pycache__/
│   │   │   ├── urls_account.cpython-312.pyc
│   │   │   ├── urls_account.cpython-313.pyc
│   │   │   ├── urls_auth.cpython-312.pyc
│   │   │   └── urls_auth.cpython-313.pyc
│   │   ├── urls_account.py
│   │   └── urls_auth.py
│   ├── views/
│   │   ├── __pycache__/
│   │   │   ├── __init__.cpython-312.pyc
│   │   │   ├── __init__.cpython-313.pyc
│   │   │   ├── views_account.cpython-312.pyc
│   │   │   ├── views_account.cpython-313.pyc
│   │   │   ├── views_auth.cpython-312.pyc
│   │   │   └── views_auth.cpython-313.pyc
│   │   ├── __init__.py
│   │   ├── views_account.py
│   │   └── views_auth.py
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py
│   ├── models.py
│   └── utils.py
├── 0003_create_default_category.py
├── Dockerfile
├── README.md
├── conftest.py
├── db.sqlite3
├── docker-compose.yml
├── fixtures_for_filling_database.json
├── manage.py
├── pytest.ini
└── requirements.txt


✅ Статус проекта

Ветка: finish
Проект полностью работает и готов к размещению / сдаче.

Чек-лист перед сдачей

- [v] Проект запускается через Docker Compose на чистой копии.
- [v] PostgreSQL используется.
- [v] Каталог: фильтры, поиск, пагинация.
- [v] Страница товара: детали, отзывы, добавление в корзину.
- [v] Корзина: управление, расчёт, проверка остатков.
- [v] Оформление заказа: создание, email, валидация.
- [v] Личный кабинет: регистрация, вход, история, редактирование.
- [v] REST API: JWT, документация, права.
- [v] Админка: аналитика, фильтры, управление.
- [v] Swagger/OpenAPI работает.
- [v] Типизация и докстринги.
- [v] Линтеры (flake8/mypy) без критичных ошибок.
- [v] Базовые тесты проходят.
- [v] README полон и понятен.
- [v] Коммиты осмысленные, ветки используются.
- [v] Чек-лист приложен.


📧 Контакты

Автор: dmitry stepenco
GitHub: https://github.com/stdimka