# 🚀 План развертывания проекта

## Предварительные требования

- Python 3.8+
- Node.js 16+ (включает npm)
- npm (устанавливается вместе с Node.js)

### Установка Node.js и npm

Если команда `npm` не найдена, установите Node.js:

1. **Скачайте Node.js:**
   - Перейдите на [nodejs.org](https://nodejs.org/)
   - Скачайте LTS версию (рекомендуется)

2. **Установите Node.js:**
   - Запустите установщик
   - Следуйте инструкциям установщика
   - Убедитесь, что опция "Add to PATH" включена

3. **Проверьте установку:**
   ```bash
   node --version
   npm --version
   ```

4. **Перезапустите терминал** после установки

**Примечание:** Если после установки команды все еще не работают:
- Перезагрузите компьютер
- Или добавьте путь к Node.js в PATH вручную: `C:\Program Files\nodejs\`

## Шаг 1: Настройка Backend (Auth API)

### 1.1. Установка зависимостей

**Windows:**
```bash
cd authapi
python -m pip install -r requirements.txt
```

**Linux/Mac:**
```bash
cd authapi
pip install -r requirements.txt
```

**Примечание:** Если команда `pip` не найдена, используйте `python -m pip` или `python3 -m pip`

### 1.2. Создание файла .env

Создайте файл `authapi/.env`:

```env
ADMIN_ACCESS_TOKEN=your_secret_admin_token_here
```

**Важно:** 
- Используйте UTF-8 без BOM для файла .env
- Замените `your_secret_admin_token_here` на свой секретный токен

### 1.3. Запуск сервера

**Windows:**
```bash
cd authapi
python -m uvicorn main:app --reload --port 8000
```

**Linux/Mac:**
```bash
cd authapi
uvicorn main:app --reload --port 8000
```

API будет доступен на `http://localhost:8000`
Документация API: `http://localhost:8000/docs`

## Шаг 2: Настройка Frontend (WebUI)

### 2.1. Установка зависимостей

**Если npm установлен:**
```bash
cd webui
npm install
```

**Если команда `npm` не найдена:**

**Вариант 1: Использовать полный путь (Windows)**
```bash
cd webui
"C:\Program Files\nodejs\npm.cmd" install
```

**Вариант 2: Добавить npm в PATH для текущей сессии (PowerShell)**
```powershell
cd webui
$env:Path += ";C:\Program Files\nodejs"
npm install
```

**Вариант 3: Установить Node.js**
- См. раздел "Предварительные требования" выше
- После установки перезапустите терминал

### 2.2. Создание файла .env

Создайте файл `webui/.env`:

```env
VITE_API_URL=http://localhost:8000
VITE_CHAT_API_URL=http://localhost:8001
```

**Важно:** 
- `VITE_API_URL` - адрес authapi (по умолчанию 8000)
- `VITE_CHAT_API_URL` - адрес chatapi (по умолчанию 8001)
- Если сервисы запущены на других портах, измените URL соответственно

### 2.3. Запуск dev сервера

```bash
cd webui
npm run dev
```

WebUI будет доступен на `http://localhost:3000` (или другом порту, если 3000 занят)

## Шаг 3: Настройка Chat API

### 3.1. Установка зависимостей

**Windows:**
```bash
cd chatapi
python -m pip install -r requirements.txt
```

**Linux/Mac:**
```bash
cd chatapi
pip install -r requirements.txt
```

**Примечание:** Если команда `pip` не найдена, используйте `python -m pip` или `python3 -m pip`

### 3.2. Создание файла .env

Создайте файл `chatapi/.env`:

```env
CONNECTION_STRING=sqlite:///database.db
```

**Важно:** 
- Используйте ту же базу данных, что и authapi (или общую БД)
- Если база данных в другой папке, укажите полный путь: `sqlite:///../authapi/database.db`

### 3.3. Запуск сервера

**Windows:**
```bash
cd chatapi
python -m uvicorn main:app --reload --port 8001
```

**Linux/Mac:**
```bash
cd chatapi
uvicorn main:app --reload --port 8001
```

Chat API будет доступен на `http://localhost:8001`
Документация API: `http://localhost:8001/docs`

## Шаг 4: Создание первого пользователя

1. Откройте `http://localhost:8000/docs` в браузере
2. Найдите эндпоинт **PUT /user** и нажмите "Try it out"
3. Заполните параметры:
   - `email`: ваш email (например, `user@example.com`)
   - `first_name`: ваше имя
   - `last_name`: ваша фамилия
   - `status`: выберите одно из значений: `STUDENT`, `TEACHER` или `ASSISTENT`
   - `access_token`: токен из `authapi/.env` (значение `ADMIN_ACCESS_TOKEN`)
4. Нажмите "Execute"
5. **Важно:** Сохраните пароль из ответа API (поле `password` в `data`) - он понадобится для входа!

## Шаг 5: Вход в систему

1. Откройте `http://localhost:3000`
2. Введите email и пароль (из шага 3)
3. Нажмите "Войти"

## Структура проекта

```
AiAgents/
├── authapi/              # Auth API (порт 8000)
│   ├── main.py          # FastAPI приложение
│   ├── requirements.txt # Python зависимости
│   └── .env            # Конфигурация (создать)
├── chatapi/              # Chat API (порт 8001)
│   ├── main.py          # FastAPI приложение
│   └── .env            # Конфигурация (создать)
├── llmapi/               # LLM API (опционально)
│   └── main.py          # FastAPI приложение
├── webui/               # Frontend
│   ├── src/            # Исходный код React
│   ├── package.json    # Node.js зависимости
│   └── .env           # Конфигурация (создать)
└── README.md          # Основная документация
```

## API Эндпоинты

### Пользователи
- `GET /user` - авторизация
- `GET /user/by_token` - получение пользователя по токену
- `PUT /user` - создание пользователя
- `PATCH /user` - обновление пользователя
- `DELETE /user` - удаление пользователя

### Чаты (Chat API - порт 8001)
- `GET /chats` - список чатов пользователя
- `PUT /chat` - создание чата
- `GET /chat?id={chat_id}` - информация о чате
- `PATCH /chat?id={chat_id}&title={title}` - обновление названия чата
- `DELETE /chat?id={chat_id}` - удаление чата

### Сообщения (Chat API - порт 8001)
- `GET /chat/history?id={chat_id}` - получение истории сообщений
- `POST /chat/send_message?id={chat_id}&text={text}` - отправка сообщения

## Продакшн развертывание

### Backend

1. Используйте production ASGI сервер (gunicorn + uvicorn workers)
2. Настройте переменные окружения
3. Используйте PostgreSQL вместо SQLite
4. Настройте CORS для конкретных доменов

### Frontend

1. Соберите проект: `npm run build`
2. Разместите файлы из `dist/` на веб-сервере
3. Настройте прокси для API запросов

## Переменные окружения

### authapi/.env
```env
ADMIN_ACCESS_TOKEN=your_secret_admin_token_here
```

**Примечание:** 
- Для продакшена рекомендуется использовать PostgreSQL вместо SQLite
- Добавьте `DATABASE_URL=postgresql://user:password@host:port/dbname` в .env

### webui/.env
```env
VITE_API_URL=http://localhost:8000
```

**Примечание:** 
- Для продакшена укажите URL вашего production API
- Например: `VITE_API_URL=https://api.yourdomain.com`

## Решение проблем

### Ошибка "pip не найден"
Используйте `python -m pip` вместо `pip`:
```bash
python -m pip install -r requirements.txt
```

### Ошибка "npm не найден"

**Решение 1: Установить Node.js**
1. Скачайте с [nodejs.org](https://nodejs.org/)
2. Установите LTS версию
3. Перезапустите терминал

**Решение 2: Использовать полный путь (Windows)**
```bash
"C:\Program Files\nodejs\npm.cmd" install
"C:\Program Files\nodejs\npm.cmd" run dev
```

**Решение 3: Добавить в PATH (PowerShell)**
```powershell
$env:Path += ";C:\Program Files\nodejs"
npm install
```

**Решение 4: Проверить установку Node.js**
```bash
node --version
```
Если команда не работает, Node.js не установлен или не в PATH

### Ошибка "Недостаточно прав" при создании пользователя
- Проверьте, что файл `authapi/.env` существует
- Убедитесь, что `ADMIN_ACCESS_TOKEN` в .env совпадает с токеном в запросе
- Перезапустите сервер после изменения .env

### Порт 8000 занят
Измените порт в команде запуска:
```bash
uvicorn main:app --reload --port 8001
```
И обновите `webui/.env`:
```env
VITE_API_URL=http://localhost:8001
```

### Порт 3000 занят
Vite автоматически предложит использовать другой порт (например, 3001)

