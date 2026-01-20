# Fitness AI Coach - Telegram Mini App

Frontend для Telegram Mini App, построенный на React + TypeScript + Vite.

## Установка

```bash
cd miniapp-frontend
npm install
```

## Разработка

```bash
# Запустить dev сервер
npm run dev

# Открыть в браузере
# http://localhost:5173
```

## Сборка

```bash
# Собрать для production
npm run build

# Предпросмотр production сборки
npm run preview
```

## Структура проекта

```
miniapp-frontend/
├── src/
│   ├── main.tsx           # Точка входа
│   ├── App.tsx            # Главный компонент
│   ├── lib/               # Библиотеки и утилиты
│   │   ├── telegram-webapp.d.ts
│   │   ├── api.ts
│   │   └── theme.ts
│   ├── components/        # React компоненты
│   │   └── ui/           # UI компоненты
│   ├── pages/            # Страницы
│   │   ├── DashboardPage.tsx
│   │   ├── DiaryPage.tsx
│   │   ├── AnalyticsPage.tsx
│   │   └── ProfilePage.tsx
│   ├── store/            # Zustand stores
│   │   ├── userStore.ts
│   │   ├── mealsStore.ts
│   │   └── themeStore.ts
│   └── styles/           # Стили
│       └── globals.css
├── public/               # Статические файлы
│   ├── manifest.json
│   └── icons/
├── index.html
├── vite.config.ts
├── tailwind.config.js
└── package.json
```

## Технологии

- **React 18** - UI библиотека
- **TypeScript** - Типизация
- **Vite** - Сборщик
- **Tailwind CSS** - Стилизация (iOS-style)
- **React Router** - Навигация
- **Zustand** - State management
- **Recharts** - Графики
- **Axios** - HTTP клиент

## Особенности

### iOS-style дизайн

Приложение использует iOS-style дизайн с:
- Скругленными углами (10px, 14px)
- Мягкими тенями
- Системными шрифтами SF Pro
- Адаптивной темной темой

### Telegram WebApp SDK

Интеграция с Telegram через WebApp SDK:
- Автоматическая инициализация
- Определение темы
- Доступ к initData для аутентификации

### Прокси для API

В dev режиме запросы к `/api` и `/uploads` проксируются на `http://localhost:8000`.

## Разработка

### Добавление новой страницы

1. Создайте компонент в `src/pages/`
2. Добавьте роут в `App.tsx`
3. Добавьте навигацию в bottom tabs

### Добавление нового store

1. Создайте файл в `src/store/`
2. Используйте Zustand для создания store
3. Импортируйте и используйте в компонентах

### Стилизация

Используйте Tailwind CSS классы и iOS-style утилиты:

```tsx
<div className="ios-card p-4">
  <button className="ios-button-primary">
    Click me
  </button>
</div>
```

## Деплой

### Vercel

```bash
# Установить Vercel CLI
npm i -g vercel

# Деплой
vercel
```

### Netlify

```bash
# Установить Netlify CLI
npm i -g netlify-cli

# Деплой
netlify deploy --prod
```

### Статический хостинг

```bash
# Собрать
npm run build

# Загрузить содержимое dist/ на сервер
```

## Настройка в Telegram

1. Откройте @BotFather
2. Выберите вашего бота
3. Используйте `/setmenubutton` или `/newapp`
4. Укажите URL вашего Mini App

## Тестирование

```bash
# Запустить тесты
npm test

# С покрытием
npm run test:coverage
```

## Troubleshooting

### Telegram WebApp SDK не загружается

Убедитесь, что скрипт подключен в `index.html`:
```html
<script src="https://telegram.org/js/telegram-web-app.js"></script>
```

### API запросы не работают

Проверьте, что Backend API запущен на порту 8000:
```bash
python -m backend_api.main
```

### Темная тема не применяется

Проверьте, что `dark` класс добавляется к `<html>`:
```javascript
document.documentElement.classList.toggle('dark', isDark)
```
