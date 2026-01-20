# 👨‍💻 Руководство для Разработчика

## 📋 Содержание
1. [Архитектура проекта](#архитектура-проекта)
2. [Структура кода](#структура-кода)
3. [Как работает бот](#как-работает-бот)
4. [Добавление новых функций](#добавление-новых-функций)
5. [Отладка](#отладка)
6. [Тестирование](#тестирование)

---

## Архитектура проекта

### Общая схема
```
Telegram User
    ↓
Telegram Bot API
    ↓
main.py (Application)
    ↓
handlers.py (Message Handlers)
    ↓
api_client.py (OpenRouter Client)
    ↓
OpenRouter API → Qwen 2.5-VL Model
    ↓
validator.py (Result Validation)
    ↓
handlers.py (Format Response)
    ↓
Telegram User
```

### Компоненты

#### 1. main.py
**Назначение:** Точка входа, инициализация бота

**Ключевые функции:**
- `main()` - создание Application, регистрация обработчиков, запуск polling

**Зависимости:**
- telegram.ext (Application, CommandHandler, MessageHandler)
- handlers (все обработчики)
- config (TELEGRAM_BOT_TOKEN)

#### 2. config.py
**Назначение:** Конфигурация и константы

**Содержит:**
- API ключи (из .env)
- Системный промпт для AI
- Текстовые сообщения
- Лимиты и настройки

**Важно:** Все изменения промпта делать здесь!

#### 3. handlers.py
**Назначение:** Обработка сообщений от пользователей

**Функции:**
- `start_command()` - обработка /start
- `help_command()` - обработка /help
- `handle_photo()` - обработка фотографий (основная логика)
- `handle_text()` - обработка текстовых сообщений
- `error_handler()` - обработка ошибок
- `format_analysis_message()` - форматирование ответа
- `get_cache_key()`, `get_from_cache()`, `save_to_cache()` - кэширование

**Кэш:**
```python
analysis_cache = {
    "hash_of_file": {
        "result": {...},
        "timestamp": datetime
    }
}
```

#### 4. api_client.py
**Назначение:** Взаимодействие с OpenRouter API

**Класс:** `OpenRouterClient`

**Методы:**
- `__init__()` - инициализация клиента
- `compress_image_if_needed()` - сжатие больших изображений
- `image_to_base64()` - конвертация в base64
- `analyze_food_image()` - основной метод анализа

**Процесс анализа:**
1. Сжатие изображения (если >5MB)
2. Конвертация в base64
3. Формирование запроса к API
4. Отправка запроса
5. Парсинг JSON ответа
6. Валидация результата
7. Возврат данных

#### 5. validator.py
**Назначение:** Валидация результатов анализа

**Класс:** `FoodAnalysisValidator`

**Методы:**
- `validate()` - главный метод валидации
- `_check_minimum_calories()` - проверка минимальной калорийности
- `_check_macros_consistency()` - проверка соответствия БЖУ
- `_check_calorie_density()` - проверка плотности калорий
- `_check_macro_ratios()` - проверка соотношений БЖУ
- `_check_components()` - проверка компонентов

**Константы:**
```python
MIN_CALORIES = {
    'breakfast': 200,
    'lunch': 400,
    'dinner': 300,
    'snack': 100
}

REALISTIC_RATIOS = {
    'protein': (10, 35),  # %
    'fat': (20, 40),      # %
    'carbs': (40, 65)     # %
}
```

---

## Структура кода

### Поток данных при обработке фото

```python
# 1. Пользователь отправляет фото
update.message.photo

# 2. handlers.py: handle_photo()
photo = update.message.photo[-1]  # Максимальное качество
file_unique_id = photo.file_unique_id

# 3. Проверка кэша
cache_key = get_cache_key(file_unique_id)
cached_result = get_from_cache(cache_key)
if cached_result:
    return cached_result

# 4. Скачивание фото
file = await context.bot.get_file(photo.file_id)
image_bytes = await file.download_as_bytearray()

# 5. Анализ через API
result = await api_client.analyze_food_image(bytes(image_bytes))

# 6. api_client.py: analyze_food_image()
# 6.1. Сжатие
image_bytes = await compress_image_if_needed(image_bytes)

# 6.2. Base64
base64_image = image_to_base64(image_bytes)

# 6.3. Запрос к API
response = await session.post(url, json=payload)

# 6.4. Парсинг JSON
parsed_data = json.loads(content)

# 6.5. Валидация
validated_data = validator.validate(parsed_data)

# 7. Сохранение в кэш
save_to_cache(cache_key, result)

# 8. Форматирование ответа
formatted_message = format_analysis_message(result)

# 9. Отправка пользователю
await message.edit_text(formatted_message)
```

---

## Как работает бот

### Запуск
```bash
python main.py
```

### Что происходит:
1. Загрузка конфигурации из .env
2. Создание Application с токеном
3. Регистрация обработчиков:
   - CommandHandler для /start, /help
   - MessageHandler для фото
   - MessageHandler для текста
   - ErrorHandler для ошибок
4. Запуск polling (опрос Telegram API каждые 10 сек)

### Обработка сообщения:
1. Telegram отправляет Update
2. Application определяет подходящий Handler
3. Handler вызывает соответствующую функцию
4. Функция обрабатывает сообщение
5. Отправляется ответ пользователю

---

## Добавление новых функций

### Пример 1: Добавить новую команду

```python
# handlers.py
async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /stats"""
    user_id = update.effective_user.id
    # Логика получения статистики
    await update.message.reply_text("Ваша статистика...")

# main.py
application.add_handler(CommandHandler("stats", stats_command))
```

### Пример 2: Добавить новую проверку в валидатор

```python
# validator.py
def _check_portion_size(self, data: Dict[str, Any]):
    """Проверяет размер порции"""
    weight = data.get('weight_grams', 0)
    
    if weight > 1000:
        self.warnings.append(
            f"⚠️ Очень большая порция: {weight}г. "
            f"Рекомендуется разделить на 2 приёма пищи."
        )

# В методе validate() добавить:
self._check_portion_size(data)
```

### Пример 3: Изменить промпт

```python
# config.py
SYSTEM_PROMPT = """
ТВОЯ НОВАЯ ИНСТРУКЦИЯ...
"""
```

### Пример 4: Добавить базу данных

```python
# database.py
import sqlite3

class FoodDatabase:
    def __init__(self):
        self.conn = sqlite3.connect('food.db')
        self.create_tables()
    
    def create_tables(self):
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS analyses (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                timestamp DATETIME,
                calories INTEGER,
                data TEXT
            )
        ''')
    
    def save_analysis(self, user_id, calories, data):
        self.conn.execute(
            'INSERT INTO analyses VALUES (?, ?, ?, ?, ?)',
            (None, user_id, datetime.now(), calories, json.dumps(data))
        )
        self.conn.commit()

# handlers.py
from database import FoodDatabase
db = FoodDatabase()

# В handle_photo() после получения результата:
db.save_analysis(user_id, result['calories_total'], result)
```

---

## Отладка

### Логирование

```python
import logging

logger = logging.getLogger(__name__)

# Уровни логирования
logger.debug("Детальная информация")
logger.info("Информационное сообщение")
logger.warning("Предупреждение")
logger.error("Ошибка")
logger.critical("Критическая ошибка")
```

### Просмотр логов

```bash
# В реальном времени
tail -f bot.log

# Последние 50 строк
tail -n 50 bot.log

# Поиск ошибок
grep ERROR bot.log

# Поиск по пользователю
grep "user_id: 12345" bot.log
```

### Отладка в IDE

```python
# Добавить точку останова
import pdb; pdb.set_trace()

# Или использовать breakpoint() в Python 3.7+
breakpoint()
```

### Тестирование API вручную

```python
# test_api.py
import asyncio
from api_client import OpenRouterClient

async def test():
    client = OpenRouterClient()
    
    # Загрузить тестовое изображение
    with open('test_image.jpg', 'rb') as f:
        image_bytes = f.read()
    
    # Анализировать
    result = await client.analyze_food_image(image_bytes)
    print(result)

asyncio.run(test())
```

---

## Тестирование

### Юнит-тесты

```python
# tests/test_validator.py
import unittest
from validator import FoodAnalysisValidator

class TestValidator(unittest.TestCase):
    def setUp(self):
        self.validator = FoodAnalysisValidator()
    
    def test_minimum_calories(self):
        data = {
            'calories_total': 100,
            'protein_g': 5,
            'fat_g': 3,
            'carbs_g': 15
        }
        result = self.validator.validate(data)
        self.assertTrue(len(result['warnings']) > 0)
    
    def test_macros_consistency(self):
        data = {
            'calories_total': 500,
            'protein_g': 50,  # 200 ккал
            'fat_g': 20,      # 180 ккал
            'carbs_g': 30     # 120 ккал
            # Итого: 500 ккал ✓
        }
        result = self.validator.validate(data)
        # Не должно быть предупреждений о несоответствии
        self.assertFalse(any('Несоответствие' in w for w in result['warnings']))

if __name__ == '__main__':
    unittest.main()
```

### Интеграционные тесты

```python
# tests/test_integration.py
import asyncio
from api_client import OpenRouterClient
from validator import FoodAnalysisValidator

async def test_full_flow():
    """Тест полного потока анализа"""
    client = OpenRouterClient()
    
    # Загрузить тестовое изображение
    with open('tests/test_images/lunch.jpg', 'rb') as f:
        image_bytes = f.read()
    
    # Анализировать
    result = await client.analyze_food_image(image_bytes)
    
    # Проверки
    assert result is not None
    assert 'calories_total' in result
    assert result['calories_total'] > 0
    assert 'components' in result
    assert len(result['components']) > 0

asyncio.run(test_full_flow())
```

### Запуск тестов

```bash
# Все тесты
python -m unittest discover tests

# Конкретный тест
python -m unittest tests.test_validator

# С покрытием
pip install coverage
coverage run -m unittest discover tests
coverage report
coverage html  # HTML отчёт в htmlcov/
```

---

## Полезные команды

### Разработка

```bash
# Создать виртуальное окружение
python3 -m venv venv

# Активировать
source venv/bin/activate

# Установить зависимости
pip install -r requirements.txt

# Запустить бота
python main.py

# Деактивировать окружение
deactivate
```

### Обновление зависимостей

```bash
# Показать устаревшие пакеты
pip list --outdated

# Обновить пакет
pip install --upgrade package_name

# Сохранить зависимости
pip freeze > requirements.txt
```

### Git

```bash
# Инициализация
git init
git add .
git commit -m "Initial commit"

# Создать .gitignore
echo ".env" >> .gitignore
echo "venv/" >> .gitignore
echo "__pycache__/" >> .gitignore
echo "*.log" >> .gitignore

# Отправить на GitHub
git remote add origin https://github.com/username/repo.git
git push -u origin main
```

---

## Лучшие практики

### 1. Безопасность
- ✅ Всегда используйте .env для ключей
- ✅ Никогда не коммитьте .env в Git
- ✅ Валидируйте входные данные
- ✅ Обрабатывайте все исключения

### 2. Код
- ✅ Следуйте PEP 8
- ✅ Пишите docstrings для функций
- ✅ Используйте type hints
- ✅ Логируйте важные события

### 3. Производительность
- ✅ Используйте async/await
- ✅ Кэшируйте результаты
- ✅ Оптимизируйте изображения
- ✅ Ограничивайте размер запросов

### 4. Тестирование
- ✅ Пишите тесты для критичной логики
- ✅ Тестируйте граничные случаи
- ✅ Используйте моки для внешних API
- ✅ Автоматизируйте тестирование

---

## Troubleshooting

### Проблема: Бот не запускается
**Решение:**
1. Проверьте .env файл
2. Проверьте токен бота
3. Проверьте зависимости: `pip install -r requirements.txt`

### Проблема: Ошибка при анализе фото
**Решение:**
1. Проверьте API ключ OpenRouter
2. Проверьте логи: `tail -f bot.log`
3. Проверьте размер фото (<5MB)

### Проблема: Неточные результаты
**Решение:**
1. Улучшите промпт в config.py
2. Добавьте проверки в validator.py
3. Используйте более качественные фото

---

## Контакты

При возникновении вопросов:
1. Проверьте документацию
2. Посмотрите логи
3. Создайте issue на GitHub
4. Напишите в поддержку

---

**Удачи в разработке! 🚀**
