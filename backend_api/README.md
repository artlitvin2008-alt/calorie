# Fitness AI Coach Backend API

REST API для Telegram Mini App, построенный на FastAPI.

## Установка

```bash
# Установить зависимости
pip install -r backend_api/requirements.txt

# Или установить все зависимости проекта
pip install -r requirements.txt
```

## Запуск

```bash
# Из корневой директории проекта
python -m backend_api.main

# Или с uvicorn напрямую
uvicorn backend_api.main:app --reload --port 8000
```

API будет доступен по адресу: http://localhost:8000

## Документация

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- Health Check: http://localhost:8000/api/health

## Структура

```
backend_api/
├── main.py              # FastAPI приложение
├── dependencies.py      # Аутентификация и зависимости
├── models.py           # Pydantic модели
├── utils.py            # Утилиты
└── routers/            # API роутеры
    ├── auth.py         # Аутентификация
    ├── user.py         # Управление пользователями
    ├── nutrition.py    # Питание и анализ
    └── analytics.py    # Аналитика
```

## API Endpoints

### Authentication
- `POST /api/auth/verify` - Проверка Telegram WebApp initData

### User Management
- `GET /api/user/profile` - Получить профиль пользователя
- `PATCH /api/user/profile` - Обновить профиль
- `GET /api/user/stats/today` - Статистика за сегодня

### Nutrition
- `POST /api/nutrition/analyze-photo` - Анализ фото еды
- `POST /api/nutrition/analyze-video` - Анализ видео еды
- `POST /api/nutrition/meals` - Создать запись о приёме пищи
- `GET /api/nutrition/meals` - Получить приёмы пищи
- `PATCH /api/nutrition/meals/{meal_id}` - Обновить приём пищи
- `DELETE /api/nutrition/meals/{meal_id}` - Удалить приём пищи

### Analytics
- `GET /api/analytics/weight` - Аналитика веса
- `GET /api/analytics/calories` - Аналитика калорий

## Аутентификация

API использует Telegram WebApp initData для аутентификации. Все защищённые эндпоинты требуют заголовок:

```
X-Telegram-Init-Data: <initData from Telegram.WebApp.initData>
```

## CORS

CORS настраивается через переменную окружения `ALLOWED_ORIGINS`:

```bash
ALLOWED_ORIGINS=http://localhost:5173,https://your-domain.com
```

## Загрузка файлов

Загруженные фото и видео сохраняются в директории `uploads/` и доступны через:

```
http://localhost:8000/uploads/<filename>
```

## Разработка

### Добавление нового эндпоинта

1. Создайте или обновите роутер в `routers/`
2. Определите Pydantic модели в `models.py`
3. Добавьте роутер в `main.py`

### Тестирование

```bash
# Запустить тесты
pytest backend_api/tests/

# С покрытием
pytest --cov=backend_api backend_api/tests/
```

## Деплой

### Docker

```bash
# Собрать образ
docker build -t fitness-api -f backend_api/Dockerfile .

# Запустить контейнер
docker run -p 8000:8000 --env-file .env fitness-api
```

### Nginx

Пример конфигурации Nginx:

```nginx
server {
    listen 80;
    server_name api.your-domain.com;

    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /uploads {
        proxy_pass http://localhost:8000;
    }
}
```
