# Fitness AI Coach - Telegram Mini App

Полноценное веб-приложение для Telegram с AI-анализом питания, построенное на гибридной архитектуре.

## 🎯 Что это?

Telegram Mini App, который работает параллельно с существующим ботом, предоставляя:
- 📸 AI-анализ фото и видео еды
- 📊 Дневник питания с историей
- 📈 Аналитика и графики
- 👤 Управление профилем и целями
- 🔄 Синхронизация между ботом и Mini App

## 🏗️ Архитектура

```
┌─────────────────┐      ┌─────────────────┐
│   Telegram Bot  │      │ Telegram Mini   │
│   (Python)      │      │ App (React/TS)  │
└───────┬─────────┘      └────────┬────────┘
        │                         │
        │ ОБЩИЙ BACKEND API       │
        │ (FastAPI)               │
        └──────────┬──────────────┘
                   │
        ┌─────────▼─────────┐
        │   SQLite Database │
        │   + AI Modules    │
        └───────────────────┘
```

## ✨ Возможности

### Backend API (✅ Готово)
- ✅ REST API на FastAPI
- ✅ Аутентификация через Telegram WebApp
- ✅ Анализ фото/видео через AI
- ✅ CRUD операции для приёмов пищи
- ✅ Аналитика и статистика
- ✅ Интеграция с существующими модулями бота

### Frontend (✅ 60% готово)
- ✅ React 18 + TypeScript + Vite
- ✅ iOS-style дизайн с Tailwind CSS
- ✅ Telegram WebApp SDK интеграция
- ✅ State management (Zustand)
- ✅ Роутинг и навигация
- ✅ API client с аутентификацией
- 🔄 Компоненты для работы с камерой
- 🔄 Графики (recharts)
- 🔄 PWA функционал

## 🚀 Быстрый старт

### 1. Backend API

```bash
# Установить зависимости
pip install -r backend_api/requirements.txt

# Запустить API
./backend_api/run.sh

# Или вручную
python -m backend_api.main

# API доступен на http://localhost:8000
# Swagger UI: http://localhost:8000/docs
```

### 2. Frontend

```bash
# Перейти в директорию frontend
cd miniapp-frontend

# Установить зависимости
npm install

# Запустить dev сервер
npm run dev

# Открыть http://localhost:5173
```

### 3. Настройка

Создайте `.env` файл из `.env.example`:

```bash
cp .env.example .env
```

Заполните переменные:
```env
TELEGRAM_BOT_TOKEN=your_bot_token
OPENROUTER_API_KEY=your_api_key
GROQ_API_KEY=your_groq_key
ALLOWED_ORIGINS=http://localhost:5173
```

## 📖 Документация

- [Backend API README](backend_api/README.md)
- [Backend Testing Guide](backend_api/TESTING.md)
- [Frontend README](miniapp-frontend/README.md)
- [Implementation Progress](TMA_IMPLEMENTATION_PROGRESS.md)
- [Spec Documents](.kiro/specs/fitness-ai-coach-tma/)

## 🧪 Тестирование

### Backend

```bash
# Запустить тесты
pytest backend_api/tests/ -v

# Тест API endpoints
python backend_api/test_api.py
```

### Frontend

```bash
cd miniapp-frontend

# Запустить тесты (когда будут добавлены)
npm test
```

## 📱 Настройка в Telegram

1. Откройте @BotFather
2. Выберите вашего бота
3. Используйте `/setmenubutton` или `/newapp`
4. Укажите URL вашего Mini App (после деплоя)

## 🛠️ Технологии

### Backend
- **FastAPI** - Modern Python web framework
- **aiosqlite** - Async SQLite
- **Pydantic** - Data validation
- **CORS** - Cross-origin support

### Frontend
- **React 18** - UI library
- **TypeScript** - Type safety
- **Vite** - Build tool
- **Tailwind CSS** - Styling
- **Zustand** - State management
- **React Router** - Navigation
- **Axios** - HTTP client
- **Recharts** - Charts (to be integrated)

### Integration
- **Telegram WebApp SDK** - Native integration
- **Existing bot modules** - PhotoAnalyzer, VideoAnalyzer

## 📊 Прогресс разработки

- ✅ Backend API: **100%**
- ✅ Frontend Infrastructure: **100%**
- 🔄 Core Features: **30%**
- ⏳ Integration: **0%**
- ⏳ Polish & Deploy: **0%**

**Общий прогресс: ~60%**

## 🎯 Следующие шаги

1. **Завершить Core Features**
   - [ ] Camera capture component
   - [ ] Charts implementation
   - [ ] Full meal CRUD UI
   - [ ] Image optimization

2. **Integration**
   - [ ] Video recording
   - [ ] Data synchronization
   - [ ] Comprehensive error handling

3. **Polish & Deploy**
   - [ ] PWA manifest
   - [ ] Performance optimization
   - [ ] Production deployment
   - [ ] Bot configuration

## 🤝 Как использовать

### Для разработки

1. Запустите Backend API (порт 8000)
2. Запустите Frontend dev server (порт 5173)
3. Откройте http://localhost:5173 в браузере
4. Используйте Swagger UI для тестирования API

### Для production

1. Соберите frontend: `npm run build`
2. Деплойте backend на сервер
3. Деплойте frontend статику (Vercel/Netlify)
4. Настройте Nginx reverse proxy
5. Укажите URL в @BotFather

## 📝 Структура проекта

```
fitness_ai_coach/
├── backend_api/           # Backend API (FastAPI)
│   ├── main.py
│   ├── routers/
│   ├── tests/
│   └── README.md
├── miniapp-frontend/      # Frontend (React)
│   ├── src/
│   │   ├── lib/          # Utilities
│   │   ├── components/   # UI components
│   │   ├── pages/        # Page components
│   │   ├── store/        # State management
│   │   └── styles/       # Styles
│   └── package.json
├── core/                  # Existing bot core
├── modules/               # Existing bot modules
└── main.py               # Existing bot
```

## 🐛 Troubleshooting

### Backend не запускается
- Проверьте, что установлены все зависимости
- Убедитесь, что порт 8000 свободен
- Проверьте .env файл

### Frontend не подключается к API
- Убедитесь, что Backend запущен
- Проверьте CORS настройки
- Проверьте proxy в vite.config.ts

### Telegram WebApp SDK не работает
- Убедитесь, что скрипт подключен в index.html
- Проверьте, что приложение открыто в Telegram
- Проверьте консоль браузера на ошибки

## 📄 Лицензия

Этот проект создан для демонстрации интеграции Telegram Mini App с существующим ботом.

## 🙏 Благодарности

- Telegram Bot API
- Telegram WebApp SDK
- FastAPI
- React
- Все используемые open-source библиотеки
