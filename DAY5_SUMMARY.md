# Day 5: API Integration (OpenRouter) - COMPLETED ✅

## Что сделано

### 1. Photo Analyzer (modules/nutrition/photo_analyzer.py) - ПОЛНОСТЬЮ РЕАЛИЗОВАН
- ✅ Интеграция с OpenRouter API
- ✅ Async архитектура
- ✅ Сжатие изображений (если >5 МБ)
- ✅ Конвертация в base64
- ✅ Создание промптов для AI
- ✅ Парсинг JSON ответов
- ✅ Очистка JSON от markdown и комментариев
- ✅ Валидация результатов
- ✅ Mock режим для тестирования
- ✅ Обработка ошибок

### 2. Photo Handler (handlers/photos.py)
- ✅ Обработка фотографий от пользователей
- ✅ Проверка регистрации
- ✅ Проверка состояния
- ✅ Скачивание фото
- ✅ Создание сессии анализа
- ✅ Вызов PhotoAnalyzer
- ✅ Сохранение результатов
- ✅ Отображение предварительного анализа
- ✅ Inline кнопка подтверждения
- ✅ Обработка ошибок

### 3. Обновлённый main.py
- ✅ Импорт handle_photo_message
- ✅ Интеграция photo handler
- ✅ Полный workflow анализа фото

## Архитектура Photo Analysis

### Полный поток анализа
```
User sends photo
    ↓
handle_photo_message()
    ↓
Check registration
    ↓
Download photo from Telegram
    ↓
Create session in database
    ↓
Set state: ANALYZING_PHOTO
    ↓
PhotoAnalyzer.analyze_photo()
    ├─ Compress image if needed
    ├─ Convert to base64
    ├─ Create analysis prompt
    ├─ Call OpenRouter API
    ├─ Parse JSON response
    ├─ Clean JSON (remove markdown, comments)
    ├─ Ensure required fields
    └─ Validate result
    ↓
Save initial_analysis to session
    ↓
Set state: WAITING_CONFIRMATION
    ↓
Display preliminary analysis + button
    ↓
User clicks "✅ Подтвердить"
    ↓
[Day 9: Save to meals table]
```

### PhotoAnalyzer Methods

#### Public Methods
- `analyze_photo(photo_bytes)` - главный метод анализа

#### Private Methods
- `_compress_image_if_needed()` - сжатие больших изображений
- `_image_to_base64()` - конвертация в base64
- `_create_analysis_prompt()` - создание промпта
- `_call_api()` - вызов OpenRouter API
- `_parse_json_response()` - парсинг JSON
- `_ensure_required_fields()` - проверка полей
- `_get_mock_analysis()` - mock данные

## OpenRouter API Integration

### Configuration
```python
API_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "qwen/qwen-2-vl-7b-instruct:free"
TEMPERATURE = 0.1  # Low for accuracy
MAX_TOKENS = 2000
```

### Headers
```python
{
    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
    "Content-Type": "application/json",
    "HTTP-Referer": "https://github.com/food-analyzer-bot",
    "X-Title": "Food Analyzer Bot"
}
```

### Request Format
```python
{
    "model": "qwen/qwen-2-vl-7b-instruct:free",
    "messages": [
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        },
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": user_prompt
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": "data:image/jpeg;base64,{base64_image}"
                    }
                }
            ]
        }
    ],
    "temperature": 0.1,
    "max_tokens": 2000
}
```

### Response Format
```json
{
    "choices": [
        {
            "message": {
                "content": "{...JSON with analysis...}"
            }
        }
    ]
}
```

## Image Processing

### Compression Strategy
1. **Check size:** If ≤5 MB, use as is
2. **Reduce quality:** Start at 85%, decrease by 10% until ≤5 MB
3. **Resize if needed:** Max dimension 1920px
4. **Convert to RGB:** Handle RGBA, LA, P modes

### Example
```
Original: 8.5 MB, 4000x3000px
    ↓
Quality 85%: 6.2 MB
    ↓
Quality 75%: 4.8 MB ✅
    ↓
Result: 4.8 MB, 4000x3000px
```

## JSON Parsing

### Cleaning Steps
1. Remove markdown blocks: ````json` and ` ``` `
2. Find JSON boundaries: `{` to `}`
3. Try parse
4. If fails:
   - Remove comments: `//...` and `/*...*/`
   - Remove trailing commas: `,}` → `}`
   - Try parse again

### Example
```python
# Input from API
"""```json
{
  "dish_name": "Пельмени",  // comment
  "calories_total": 625,
}
```"""

# After cleaning
{
  "dish_name": "Пельмени",
  "calories_total": 625
}
```

## Prompts

### System Prompt (config.py)
```
ТЫ — ЭКСПЕРТНЫЙ АНАЛИЗАТОР ЕДЫ С 20-ЛЕТНИМ ОПЫТОМ ДИЕТОЛОГИИ.

ТВОЯ ЗАДАЧА: Максимально точно проанализировать фотографию еды 
и найти ВСЕ компоненты без пропусков.

КРИТИЧЕСКИ ВАЖНО:
1. ВСЕГДА ищи ВСЕ элементы на фото
2. Для каждого компонента определи точное название и вес
3. Используй РЕАЛЬНЫЕ данные калорийности
4. Проверь соответствие БЖУ и калорий
5. Верни ответ СТРОГО в JSON формате
```

### User Prompt
```
ПРОАНАЛИЗИРУЙ ЭТУ ФОТОГРАФИЮ ЕДЫ МАКСИМАЛЬНО ТОЧНО:

ОБЯЗАТЕЛЬНЫЕ ТРЕБОВАНИЯ:
1. Найди ВСЕ компоненты (включая хлеб, соусы, напитки)
2. Оцени вес КАЖДОГО компонента (используй столовые приборы для масштаба)
3. Для КАЖДОГО компонента рассчитай калорийность, БЖУ
4. Используй ТОЧНЫЕ названия
5. Если видишь хлеб — ОБЯЗАТЕЛЬНО включи в расчёт!

ВАЖНО: Верни ответ СТРОГО в JSON формате без дополнительного текста.
```

## Error Handling

### API Errors
- **Status != 200:** Log error, return None
- **No choices:** Log error, return None
- **Network error:** Log error, return None
- **Timeout (60s):** Handled by aiohttp

### JSON Errors
- **Not found:** Try to find `{...}` boundaries
- **Parse error:** Clean and retry
- **Still fails:** Log and return None

### Photo Errors
- **Too large:** Compress automatically
- **Invalid format:** Convert to RGB
- **Download fails:** Show error to user

## Mock Mode

### Activation
```python
# In .env
USE_MOCK_API=true

# Or in code
photo_analyzer = PhotoAnalyzer(use_mock=True)
```

### Mock Data
```python
{
    "components": [
        {
            "name": "Пельмени",
            "weight_g": 250,
            "calories": 625,
            "protein_g": 30,
            "fat_g": 25,
            "carbs_g": 70,
            "confidence": 0.85
        },
        {
            "name": "Сметана",
            "weight_g": 30,
            "calories": 60,
            "protein_g": 2,
            "fat_g": 3,
            "carbs_g": 2,
            "confidence": 0.90
        }
    ],
    "dish_name": "Пельмени со сметаной",
    "weight_grams": 280,
    "calories_total": 685,
    "calories_per_100g": 245,
    "protein_g": 32,
    "fat_g": 28,
    "carbs_g": 72,
    "health_score": 5
}
```

## Статистика

- **Файлов создано:** 2
- **Строк кода:** ~400
- **API методов:** 8
- **Обработчиков:** 1

## Тестирование

### В Telegram
1. Отправь боту `/start`
2. Пройди регистрацию `/setup`
3. Отправь фото еды
4. Получи анализ с компонентами
5. Нажми "✅ Подтвердить"

### Mock режим
```bash
# В .env
USE_MOCK_API=true

# Перезапусти бота
venv/bin/python main_new.py
```

### Real API режим
```bash
# В .env
USE_MOCK_API=false

# Перезапусти бота
venv/bin/python main_new.py
```

## Следующие шаги (Day 6)

### Preliminary Analysis Display
- [ ] Улучшить форматирование компонентов
- [ ] Добавить confidence indicators
- [ ] Показывать warnings если есть
- [ ] Добавить кнопку "✏️ Исправить"

### Готовность к Day 6
- ✅ API интеграция работает
- ✅ Фото анализируются
- ✅ Результаты отображаются
- ✅ Inline кнопка работает
- ⏳ Нужно улучшить отображение

## Известные ограничения

- ✅ API интеграция работает!
- ✅ Анализ фото работает!
- ✅ Mock режим работает!
- 🚧 Подтверждение анализа - заглушка (Day 9)
- 🚧 Коррекции пока не работают (Day 7-8)

## Файлы

### Созданные на Day 5
- `modules/nutrition/photo_analyzer.py` - полная реализация
- `handlers/photos.py` - обработчик фото

### Обновлённые
- `main_new.py` - интеграция photo handler

### Из предыдущих дней
- Day 1: core/* (database, state_machine, session_manager, user_manager)
- Day 2: handlers/commands.py, handlers/registration.py, utils/formatters.py, config.py
- Day 3: utils/keyboards.py, handlers/callbacks.py
- Day 4: utils/validators.py, modules/nutrition/calorie_calculator.py

## Примеры использования

### Analyze Photo
```python
from modules/nutrition.photo_analyzer import PhotoAnalyzer

analyzer = PhotoAnalyzer(use_mock=False)
result = await analyzer.analyze_photo(photo_bytes)

if result:
    print(f"Dish: {result['dish_name']}")
    print(f"Calories: {result['calories_total']}")
    print(f"Components: {len(result['components'])}")
```

### With Mock Data
```python
analyzer = PhotoAnalyzer(use_mock=True)
result = await analyzer.analyze_photo(photo_bytes)
# Returns mock data instantly
```

## Время выполнения

Day 5 ✅ - API Integration завершён!

**Бот работает (Process ID: 11)** и может анализировать фотографии еды!

## Прогресс по плану (2 недели)

**Неделя 1:**
- ✅ Day 1: Infrastructure (БД, State Machine, Core)
- ✅ Day 2: User Management (Команды, Регистрация)
- ✅ Day 3: Telegram Handlers (Inline кнопки, Callbacks)
- ✅ Day 4: Validators & Nutrition Structure
- ✅ Day 5: API Integration (OpenRouter) ✅

**Неделя 2:**
- ⏳ Day 6: Preliminary Analysis Display
- ⏳ Day 7-8: Correction System
- ⏳ Day 9: Final Analysis & Save
- ⏳ Day 10-14: Testing & Polish

**Прогресс: 5/14 дней (35.7%)**

🎉 **Первая неделя завершена!** Бот может анализировать фотографии еды!
