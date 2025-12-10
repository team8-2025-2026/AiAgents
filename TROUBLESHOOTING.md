# Решение проблем с запуском проекта

## Проблема: На localhost:3000 ничего не отображается

### Решение 1: Проверьте консоль браузера

1. Откройте `http://localhost:3000` в браузере
2. Нажмите `F12` для открытия инструментов разработчика
3. Перейдите на вкладку **Console**
4. Проверьте наличие ошибок (красные сообщения)

### Решение 2: Очистите кэш браузера

1. Нажмите `Ctrl + Shift + Delete`
2. Выберите "Кэшированные изображения и файлы"
3. Нажмите "Очистить данные"
4. Обновите страницу (`F5` или `Ctrl + R`)

### Решение 3: Проверьте, что все сервисы запущены

Откройте три отдельных окна терминала и проверьте:

**Окно 1 - Auth API:**
```powershell
cd authapi
python -m uvicorn main:app --reload --port 8000
```
Должно быть: `Uvicorn running on http://127.0.0.1:8000`

**Окно 2 - Chat API:**
```powershell
cd chatapi
python -m uvicorn main:app --reload --port 8001
```
Должно быть: `Uvicorn running on http://127.0.0.1:8001`

**Окно 3 - WebUI:**
```powershell
cd webui
npm run dev
```
Должно быть: `Local: http://localhost:3000/`

### Решение 4: Проверьте .env файлы

**authapi/.env:**
```
ADMIN_ACCESS_TOKEN=your_secret_admin_token_here
```

**chatapi/.env:**
```
CONNECTION_STRING=sqlite:///../authapi/database.db
```

**webui/.env:**
```
VITE_API_URL=http://localhost:8000
VITE_CHAT_API_URL=http://localhost:8001
```

### Решение 5: Переустановите зависимости

**WebUI:**
```powershell
cd webui
rm -r node_modules
npm install
npm run dev
```

**Auth API и Chat API:**
```powershell
cd authapi
python -m pip install -r requirements.txt --force-reinstall

cd ..\chatapi
python -m pip install -r requirements.txt --force-reinstall
```

### Решение 6: Проверьте порты

Убедитесь, что порты 3000, 8000 и 8001 не заняты другими приложениями:

```powershell
netstat -ano | findstr ":3000"
netstat -ano | findstr ":8000"
netstat -ano | findstr ":8001"
```

Если порты заняты, либо остановите другие приложения, либо измените порты в конфигурации.

## Проблема: Ошибки CORS

Если видите ошибки CORS в консоли браузера, убедитесь, что:
- Auth API и Chat API запущены
- В `authapi/main.py` и `chatapi/main.py` настроен CORS middleware

## Проблема: "Cannot GET /"

Это означает, что Vite dev server не запущен или не работает правильно.
Перезапустите WebUI:

```powershell
cd webui
npm run dev
```

## Проблема: Белый экран без ошибок

1. Откройте консоль браузера (`F12`)
2. Проверьте вкладку **Network**
3. Убедитесь, что файлы загружаются (статус 200)
4. Проверьте, что `main.jsx` загружается

## Проблема: Переменные окружения не работают

Vite требует перезапуск dev server после изменения `.env` файлов:

1. Остановите WebUI (`Ctrl + C`)
2. Запустите снова: `npm run dev`

## Полезные команды для диагностики

**Проверка работы API:**
```powershell
# Auth API
Invoke-WebRequest -Uri http://localhost:8000/docs

# Chat API
Invoke-WebRequest -Uri http://localhost:8001/docs
```

**Проверка работы WebUI:**
```powershell
Invoke-WebRequest -Uri http://localhost:3000
```

**Просмотр логов:**
- Откройте окна терминалов, где запущены сервисы
- Проверьте сообщения об ошибках

