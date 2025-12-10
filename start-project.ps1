# Скрипт для запуска проекта AiAgents
# Использование: .\start-project.ps1

Write-Host "=== Запуск проекта AiAgents ===" -ForegroundColor Green
Write-Host ""

# Проверка наличия .env файлов
Write-Host "Проверка .env файлов..." -ForegroundColor Yellow

if (-not (Test-Path "authapi\.env")) {
    Write-Host "Создание authapi\.env..." -ForegroundColor Yellow
    @"
ADMIN_ACCESS_TOKEN=your_secret_admin_token_here
"@ | Out-File -FilePath "authapi\.env" -Encoding utf8
    Write-Host "✓ Создан authapi\.env (не забудьте изменить ADMIN_ACCESS_TOKEN!)" -ForegroundColor Green
}

if (-not (Test-Path "chatapi\.env")) {
    Write-Host "Создание chatapi\.env..." -ForegroundColor Yellow
    @"
CONNECTION_STRING=sqlite:///../authapi/database.db
"@ | Out-File -FilePath "chatapi\.env" -Encoding utf8
    Write-Host "✓ Создан chatapi\.env" -ForegroundColor Green
}

if (-not (Test-Path "webui\.env")) {
    Write-Host "Создание webui\.env..." -ForegroundColor Yellow
    @"
VITE_API_URL=http://localhost:8000
VITE_CHAT_API_URL=http://localhost:8001
"@ | Out-File -FilePath "webui\.env" -Encoding utf8
    Write-Host "✓ Создан webui\.env" -ForegroundColor Green
}

Write-Host ""
Write-Host "=== Установка зависимостей ===" -ForegroundColor Green
Write-Host ""

# Установка зависимостей для authapi
Write-Host "Установка зависимостей для authapi..." -ForegroundColor Yellow
Set-Location authapi
python -m pip install -r requirements.txt --quiet
if ($LASTEXITCODE -ne 0) {
    Write-Host "✗ Ошибка установки зависимостей для authapi" -ForegroundColor Red
    Set-Location ..
    exit 1
}
Set-Location ..
Write-Host "✓ Зависимости authapi установлены" -ForegroundColor Green

# Установка зависимостей для chatapi
Write-Host "Установка зависимостей для chatapi..." -ForegroundColor Yellow
Set-Location chatapi
python -m pip install -r requirements.txt --quiet
if ($LASTEXITCODE -ne 0) {
    Write-Host "✗ Ошибка установки зависимостей для chatapi" -ForegroundColor Red
    Set-Location ..
    exit 1
}
Set-Location ..
Write-Host "✓ Зависимости chatapi установлены" -ForegroundColor Green

# Установка зависимостей для webui
Write-Host "Установка зависимостей для webui..." -ForegroundColor Yellow
Set-Location webui
if (-not (Test-Path "node_modules")) {
    npm install --silent
    if ($LASTEXITCODE -ne 0) {
        Write-Host "✗ Ошибка установки зависимостей для webui" -ForegroundColor Red
        Set-Location ..
        exit 1
    }
}
Set-Location ..
Write-Host "✓ Зависимости webui установлены" -ForegroundColor Green

Write-Host ""
Write-Host "=== Запуск сервисов ===" -ForegroundColor Green
Write-Host ""
Write-Host "Сервисы будут запущены в отдельных окнах PowerShell" -ForegroundColor Cyan
Write-Host "Для остановки закройте соответствующие окна" -ForegroundColor Cyan
Write-Host ""

# Запуск Auth API
Write-Host "Запуск Auth API на порту 8000..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD\authapi'; python -m uvicorn main:app --reload --port 8000"
Start-Sleep -Seconds 2

# Запуск Chat API
Write-Host "Запуск Chat API на порту 8001..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD\chatapi'; python -m uvicorn main:app --reload --port 8001"
Start-Sleep -Seconds 2

# Запуск WebUI
Write-Host "Запуск WebUI на порту 3000..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD\webui'; npm run dev"
Start-Sleep -Seconds 2

Write-Host ""
Write-Host "=== Сервисы запущены! ===" -ForegroundColor Green
Write-Host ""
Write-Host "Доступные адреса:" -ForegroundColor Cyan
Write-Host "  - Auth API:    http://localhost:8000" -ForegroundColor White
Write-Host "  - Auth API Docs: http://localhost:8000/docs" -ForegroundColor White
Write-Host "  - Chat API:    http://localhost:8001" -ForegroundColor White
Write-Host "  - Chat API Docs: http://localhost:8001/docs" -ForegroundColor White
Write-Host "  - WebUI:       http://localhost:3000" -ForegroundColor White
Write-Host ""
Write-Host "Следующие шаги:" -ForegroundColor Yellow
Write-Host "  1. Откройте http://localhost:8000/docs" -ForegroundColor White
Write-Host "  2. Создайте первого пользователя через PUT /user" -ForegroundColor White
Write-Host "  3. Сохраните пароль из ответа" -ForegroundColor White
Write-Host "  4. Откройте http://localhost:3000 и войдите" -ForegroundColor White
Write-Host ""

