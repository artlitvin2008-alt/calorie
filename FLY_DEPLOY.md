# 🚀 Деплой на Fly.io (Бесплатно)

## ✅ Преимущества Fly.io

- ✅ Полностью бесплатный (3 VM бесплатно)
- ✅ Не засыпает (в отличие от Render)
- ✅ Быстрый старт
- ✅ Простая настройка через CLI

---

## 📦 Шаг 1: Установить Fly CLI

### macOS:
```bash
brew install flyctl
```

### Или через curl:
```bash
curl -L https://fly.io/install.sh | sh
```

---

## 🔐 Шаг 2: Войти в Fly.io

```bash
flyctl auth login
```

Откроется браузер для входа через GitHub (используйте **artlitvin2008-alt**)

---

## 🚀 Шаг 3: Задеплоить приложение

### 3.1 Перейти в папку backend

```bash
cd backend_api
```

### 3.2 Запустить деплой

```bash
flyctl launch
```

### 3.3 Ответить на вопросы:

```
? Choose an app name: calorie-backend
? Choose a region: Frankfurt, Germany (fra)
? Would you like to set up a PostgreSQL database? No
? Would you like to set up an Upstash Redis database? No
? Would you like to deploy now? No
```

### 3.4 Добавить переменные окружения

```bash
flyctl secrets set TELEGRAM_BOT_TOKEN="ваш_токен_бота"
flyctl secrets set GROQ_API_KEY="ваш_groq_ключ"
flyctl secrets set OPENROUTER_API_KEY="ваш_openrouter_ключ"
flyctl secrets set ALLOWED_ORIGINS="*"
```

Замените значения на ваши реальные ключи из .env файла!

### 3.5 Задеплоить

```bash
flyctl deploy
```

---

## 📝 Шаг 4: Получить URL

После успешного деплоя:

```bash
flyctl info
```

URL будет типа: `https://calorie-backend.fly.dev`

---

## ✅ Проверить

```bash
curl https://calorie-backend.fly.dev/api/health
```

Должно вернуть: `{"status":"healthy"...}`

---

## 🎯 Готово!

Backend задеплоен на Fly.io и работает 24/7 бесплатно!

---

**Время: 5 минут**  
**Стоимость: $0**  
**Не засыпает!** 🚀
