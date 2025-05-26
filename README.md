# Foodgram - Продуктовый помощник

## Описание проекта

Foodgram - это веб-приложение для публикации рецептов. Пользователи могут:
- Создавать и публиковать рецепты с фотографиями
- Добавлять рецепты в избранное
- Подписываться на других авторов
- Формировать список покупок на основе выбранных рецептов
- Скачивать список ингредиентов для покупок в текстовом формате
- Получать короткие ссылки на рецепты

## Технологии

- **Backend**: Django 4.2, Django REST Framework, PostgreSQL
- **Frontend**: React, JavaScript
- **Инфраструктура**: Docker, Docker Compose, Nginx, Gunicorn
- **База данных**: PostgreSQL
- **API**: RESTful API с документацией

## Запуск

### 1. Клонирование репозитория
```bash
git clone https://github.com/aJLaxzzz/foodgram-st
cd foodgram-st
```

### 2. Настройка переменных окружения
Создайте файл `infra/.env` с настройками:
```bash
POSTGRES_DB=foodgram
POSTGRES_USER=foodgram_user
POSTGRES_PASSWORD=foodgram_password
DB_HOST=db
DB_PORT=5432
SECRET_KEY=jsn!a=&x*ru4qpdhjpegle45i_zvfr=axu3&t)-sg+3bsukw@f
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0

```

### 3. Запуск проекта
```bash
# Сборка и запуск всех контейнеров
docker compose up -d
```

### 4. Инициализация данных
```bash
# Загрузка ингредиентов 
docker compose exec backend python load_ingredients.py

# Загрузка тестовых данных 
docker compose exec backend python load_test_data.py

# Создание суперпользователя
docker compose exec backend python manage.py createsuperuser


```

### 5. Проверка работы
Откройте в браузере:
- **Фронтенд**: http://localhost/
- **API**: http://localhost/api/
- **Админка**: http://localhost/admin/
- **Документация API**: http://localhost/api/docs/

## Тестовые данные

После загрузки тестовых данных будут доступны:

**Пользователи:**
- Администратор: `admin@example.com` / `admin` 
- Пользователь: `user@example.com` / `user` 

**Рецепты:**
- Борщ
- Блины классические

## Структура проекта

```
foodgram-st/
├── backend/                 # Django приложение
│   ├── api/                # API эндпоинты
│   ├── recipes/            # Модели рецептов
│   ├── users/              # Модели пользователей
│   ├── foodgram/           # Настройки Django
│   ├── requirements.txt    # Python зависимости
│   ├── Dockerfile         # Образ для backend
│   └── entrypoint.sh      # Скрипт инициализации
├── frontend/               # React приложение
│   ├── build/             # Собранные статические файлы
│   └── ...
├── infra/                  # Инфраструктура
│   ├── docker-compose.yml # Конфигурация Docker
│   ├── nginx.conf         # Настройки Nginx
│   └── .env              # Переменные окружения
├── data/                   # Данные
│   └── ingredients.csv    # Список ингредиентов
└── README.md              # Этот файл
```



## Автор

Черных Тимофей Юрьевич

