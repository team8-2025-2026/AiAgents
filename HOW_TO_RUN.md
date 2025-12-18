# Как запустить проект

## Предварительные требования

- Python 3.8+
- Node.js 16+
- npm

## Проверка структуры проекта

После клонирования проекта убедитесь, что все файлы на месте:

**Mac/Linux:**
```bash
# Проверьте структуру проекта
ls -la
# Должны быть папки: authapi, chatapi, webui, llmapi

# Проверьте наличие requirements.txt
ls authapi/requirements.txt
ls chatapi/requirements.txt
```

**Windows:**
```bash
# Проверьте структуру проекта
dir
# Должны быть папки: authapi, chatapi, webui, llmapi

# Проверьте наличие requirements.txt
dir authapi\requirements.txt
dir chatapi\requirements.txt
```

Если файлы отсутствуют, выполните:
```bash
git pull origin main
```

## Шаг 1: Настройка Auth API (порт 8000)

### 1.1. Установка зависимостей

**Важно:** Убедитесь, что вы находитесь в папке `authapi` перед установкой!

**Windows:**
```bash
cd authapi
python -m pip install -r requirements.txt
```

**Mac/Linux:**
```bash
cd authapi
# Проверьте, что файл существует:
ls requirements.txt
# Если файл есть, установите зависимости:
python3 -m pip install -r requirements.txt
# или
pip3 install -r requirements.txt
```

**Если файл не найден:**
- Убедитесь, что вы в правильной папке: `pwd` (Mac/Linux) или `cd` (Windows)
- Проверьте, что проект полностью склонирован: `git pull origin main`

### 1.2. Создание .env файла

**Mac/Linux:**
```bash
cd authapi
cat > .env << EOF
ADMIN_ACCESS_TOKEN=your_secret_admin_token_here
EOF
```

**Windows (PowerShell):**
```powershell
cd authapi
@"
ADMIN_ACCESS_TOKEN=your_secret_admin_token_here
"@ | Out-File -FilePath .env -Encoding utf8
```

**Windows (CMD):**
```cmd
cd authapi
echo ADMIN_ACCESS_TOKEN=your_secret_admin_token_here > .env
```

**Или вручную:**
- Создайте файл `authapi/.env` в текстовом редакторе
- Добавьте строку: `ADMIN_ACCESS_TOKEN=your_secret_admin_token_here`
- Сохраните файл

### 1.3. Запуск

**Windows:**
```bash
cd authapi
python -m uvicorn main:app --reload --port 8000
```

**Mac/Linux:**
```bash
cd authapi
python3 -m uvicorn main:app --reload --port 8000
# или
uvicorn main:app --reload --port 8000
```

API будет доступен на `http://localhost:8000`
Документация: `http://localhost:8000/docs`

## Шаг 2: Настройка Chat API (порт 8001)

### 2.1. Установка зависимостей

**Важно:** Убедитесь, что вы находитесь в папке `chatapi` перед установкой!

**Windows:**
```bash
cd chatapi
python -m pip install -r requirements.txt
```

**Mac/Linux:**
```bash
cd chatapi
# Проверьте, что файл существует:
ls requirements.txt
# Если файл есть, установите зависимости:
python3 -m pip install -r requirements.txt
# или
pip3 install -r requirements.txt
```

**Если файл не найден:**
- Убедитесь, что вы в правильной папке: `pwd` (Mac/Linux)
- Проверьте, что проект полностью склонирован: `git pull origin main`

### 2.2. Создание .env файла

**Mac/Linux:**
```bash
cd chatapi
cat > .env << EOF
CONNECTION_STRING=sqlite:///database.db
EOF
```

**Windows (PowerShell):**
```powershell
cd chatapi
@"
CONNECTION_STRING=sqlite:///database.db
"@ | Out-File -FilePath .env -Encoding utf8
```

**Windows (CMD):**
```cmd
cd chatapi
echo CONNECTION_STRING=sqlite:///database.db > .env
```

**Или вручную:**
- Создайте файл `chatapi/.env` в текстовом редакторе
- Добавьте строку: `CONNECTION_STRING=sqlite:///database.db`
- Сохраните файл

**Важно:** 
- Используйте ту же базу данных, что и authapi (или общую БД)
- Если база данных находится в папке authapi, используйте: `CONNECTION_STRING=sqlite:///../authapi/database.db`
- **Файл .env должен быть создан ДО запуска сервера, иначе будет ошибка!**

### 2.3. Запуск

**Windows:**
```bash
cd chatapi
python -m uvicorn main:app --reload --port 8001
```

**Mac/Linux:**
```bash
cd chatapi
python3 -m uvicorn main:app --reload --port 8001
# или
uvicorn main:app --reload --port 8001
```

API будет доступен на `http://localhost:8001`
Документация: `http://localhost:8001/docs`

## Шаг 3: Настройка Frontend (WebUI)

### 3.1. Установка зависимостей
```bash
cd webui
npm install
```

### 3.2. Создание .env файла

**Mac/Linux:**
```bash
cd webui
cat > .env << EOF
VITE_API_URL=http://localhost:8000
VITE_CHAT_API_URL=http://localhost:8001
EOF
```

**Windows (PowerShell):**
```powershell
cd webui
@"
VITE_API_URL=http://localhost:8000
VITE_CHAT_API_URL=http://localhost:8001
"@ | Out-File -FilePath .env -Encoding utf8
```

**Windows (CMD):**
```cmd
cd webui
echo VITE_API_URL=http://localhost:8000 > .env
echo VITE_CHAT_API_URL=http://localhost:8001 >> .env
```

**Или вручную:**
- Создайте файл `webui/.env` в текстовом редакторе
- Добавьте строки:
  ```
  VITE_API_URL=http://localhost:8000
  VITE_CHAT_API_URL=http://localhost:8001
  ```
- Сохраните файл

### 3.3. Запуск
```bash
cd webui
npm run dev
```

WebUI будет доступен на `http://localhost:3000` (или другом порту)

## Шаг 4: Создание первого пользователя

1. Откройте `http://localhost:8000/docs`
2. Найдите эндпоинт **PUT /user** и нажмите "Try it out"
3. Заполните параметры:
   - `email`: ваш email
   - `first_name`: ваше имя
   - `last_name`: ваша фамилия
   - `status`: `STUDENT` или `ASSISTENT`
   - `access_token`: токен из `authapi/.env` (ADMIN_ACCESS_TOKEN)
4. Нажмите "Execute"
5. **Сохраните пароль** из ответа API - он понадобится для входа!

## Шаг 5: Вход в систему

1. Откройте `http://localhost:3000`
2. Введите email и пароль (из шага 4)
3. Нажмите "Войти"

## Порядок запуска сервисов

1. **Auth API** (порт 8000) - сначала
2. **Chat API** (порт 8001) - второй
3. **WebUI** (порт 3000) - последний

## Проверка работы

- Auth API: `http://localhost:8000/docs`
- Chat API: `http://localhost:8001/docs`
- WebUI: `http://localhost:3000`

## Примечания

- Все сервисы должны быть запущены одновременно
- База данных должна быть общей для authapi и chatapi
- Используйте UTF-8 без BOM для .env файлов

