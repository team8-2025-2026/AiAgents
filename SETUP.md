# Инструкция по установке и запуску

## Предварительные требования

- Python 3.8 или выше
- Node.js 16 или выше
- npm или yarn

## Установка

### 1. Установка зависимостей Auth API

**Для Windows (PowerShell):**
```powershell
cd authapi
python -m pip install -r requirements.txt
```

**Для Linux/Mac:**
```bash
cd authapi
pip install -r requirements.txt
```

### 2. Настройка переменных окружения для Auth API

Создайте файл `.env` в папке `authapi/`:

```env
ADMIN_ACCESS_TOKEN=your_secret_admin_token_here
```

### 3. Запуск Auth API

**Для Windows (PowerShell):**
```powershell
cd authapi
python -m uvicorn main:app --reload --port 8000
```

**Для Linux/Mac:**
```bash
cd authapi
uvicorn main:app --reload --port 8000
```

API будет доступен на `http://localhost:8000`

Документация API доступна на `http://localhost:8000/docs`

### 4. Установка зависимостей WebUI

```bash
cd webui
npm install
```

### 5. Настройка переменных окружения для WebUI

Создайте файл `.env` в папке `webui/`:

```env
VITE_API_URL=http://localhost:8000
```

### 6. Запуск WebUI

```bash
cd webui
npm run dev
```

WebUI будет доступен на `http://localhost:3000`

## Использование

1. Откройте браузер и перейдите на `http://localhost:3000`
2. Для входа используйте email и пароль (создание аккаунтов доступно только через поддержку)
3. После входа вы увидите интерфейс в зависимости от вашей роли:
   - **Студент**: может создавать, переименовывать и удалять чаты
   - **Учитель**: может просматривать чаты студентов с фильтрацией
   - **Ассистент**: может управлять пользователями и просматривать все чаты

## Создание первого пользователя

Для создания первого пользователя (например, ассистента) можно использовать Python скрипт или напрямую через API:

```python
import requests

# Создание пользователя через API (требует ADMIN_ACCESS_TOKEN)
response = requests.put(
    "http://localhost:8000/user",
    params={
        "email": "admin@example.com",
        "first_name": "Admin",
        "last_name": "User",
        "status": "ASSISTENT",
        "access_token": "your_secret_admin_token_here"
    }
)

print(response.json())
```

Или используйте Swagger UI на `http://localhost:8000/docs` для тестирования API.

## Структура базы данных

База данных SQLite создается автоматически в файле `authapi/database.db` при первом запуске.

