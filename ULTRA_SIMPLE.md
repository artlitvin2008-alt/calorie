# 🎯 САМАЯ ПРОСТАЯ ИНСТРУКЦИЯ

## Что делать прямо сейчас:

---

## 1️⃣ RAILWAY (Backend)

### Откройте: https://railway.app

### Что нажимать:

```
1. "Start a New Project"
2. "Login with GitHub" 
3. "New Project"
4. "Deploy from GitHub repo"
5. Выбрать ваш репозиторий
```

### После деплоя:

```
1. Settings → Root Directory → Написать: backend_api
2. Variables → Add Variable:
   
   TELEGRAM_BOT_TOKEN = ваш_токен
   GROQ_API_KEY = ваш_ключ
   ALLOWED_ORIGINS = *

3. Settings → Networking → Generate Domain
4. СКОПИРОВАТЬ URL!
```

**Ваш Backend URL: _______________________________**

---

## 2️⃣ VERCEL (Frontend)

### Откройте: https://vercel.com

### Что нажимать:

```
1. "Sign Up"
2. "Continue with GitHub"
3. "Add New..." → "Project"
4. Выбрать ваш репозиторий → "Import"
```

### На странице настройки:

```
1. Framework Preset: Vite
2. Root Directory: Edit → miniapp-frontend
3. Environment Variables → Add:
   
   Name: VITE_API_URL
   Value: https://ваш-url-из-railway.railway.app/api
   
   ⚠️ Замените на реальный URL из Railway!

4. "Deploy"
5. Дождаться (1-2 минуты)
6. СКОПИРОВАТЬ URL!
```

**Ваш Frontend URL: _______________________________**

---

## 3️⃣ ОБНОВИТЬ CORS

### Вернуться в Railway:

```
1. Variables
2. Найти ALLOWED_ORIGINS
3. Изменить на: https://ваш-url-из-vercel.vercel.app,https://web.telegram.org
4. Save
```

---

## 4️⃣ BOTFATHER

### Открыть Telegram → @BotFather

### Отправить команды:

```
/mybots
→ Выбрать вашего бота
→ Bot Settings
→ Menu Button
→ Configure Menu Button
→ Ввести: https://ваш-url-из-vercel.vercel.app
→ Ввести: Open App
```

---

## 5️⃣ ПРОВЕРИТЬ

### В браузере:

```
https://ваш-url-из-railway.railway.app/api/health
```

Должно показать: `{"status":"healthy"...}`

### В Telegram:

```
1. Открыть вашего бота
2. Нажать Start
3. Нажать Menu (≡)
4. Выбрать "Open App"
```

---

## ✅ ГОТОВО!

Если открылось приложение - всё работает! 🎉

---

## ❌ НЕ РАБОТАЕТ?

### Backend не отвечает:
- Проверьте Root Directory = `backend_api`
- Проверьте переменные окружения
- Посмотрите логи в Railway

### Frontend показывает ошибки:
- Проверьте VITE_API_URL (должен заканчиваться на `/api`)
- Проверьте что backend доступен
- Проверьте CORS

### Mini App не открывается:
- Проверьте URL в BotFather
- Очистите кэш Telegram
- Попробуйте в другом браузере

---

## 📝 ВАЖНЫЕ ССЫЛКИ

Railway Dashboard: https://railway.app/dashboard  
Vercel Dashboard: https://vercel.com/dashboard  
BotFather: https://t.me/BotFather

---

**Время: 15 минут**  
**Стоимость: Бесплатно**  
**Сложность: Легко**

**Поехали! 🚀**
