@echo off
REM Простой скрипт для запуска всех сервисов
REM Использование: start-project-simple.bat

echo === Запуск проекта AiAgents ===
echo.

REM Проверка и создание .env файлов
if not exist "authapi\.env" (
    echo Создание authapi\.env...
    echo ADMIN_ACCESS_TOKEN=your_secret_admin_token_here > authapi\.env
)

if not exist "chatapi\.env" (
    echo Создание chatapi\.env...
    echo CONNECTION_STRING=sqlite:///../authapi/database.db > chatapi\.env
)

if not exist "webui\.env" (
    echo Создание webui\.env...
    echo VITE_API_URL=http://localhost:8000 > webui\.env
    echo VITE_CHAT_API_URL=http://localhost:8001 >> webui\.env
)

echo.
echo === Запуск сервисов ===
echo.

REM Запуск Auth API
start "Auth API (8000)" cmd /k "cd authapi && python -m uvicorn main:app --reload --port 8000"

REM Запуск Chat API
start "Chat API (8001)" cmd /k "cd chatapi && python -m uvicorn main:app --reload --port 8001"

REM Запуск WebUI
start "WebUI (3000)" cmd /k "cd webui && npm run dev"

echo.
echo Сервисы запущены в отдельных окнах!
echo.
echo Доступные адреса:
echo   - Auth API: http://localhost:8000
echo   - Chat API: http://localhost:8001
echo   - WebUI:    http://localhost:3000
echo.
pause

