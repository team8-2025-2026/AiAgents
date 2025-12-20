# Быстрый старт с GigaChat API

## Что было сделано

1. ✅ Создан модуль `llmapi/gigachat_client.py` для работы с GigaChat API
2. ✅ Обновлен `llmapi/main.py` для поддержки GigaChat API
3. ✅ Обновлен `chatapi/main.py` для использования LLM API вместо заглушки
4. ✅ Добавлены необходимые зависимости
5. ✅ Создана документация

## Быстрая настройка

### 1. Получите учетные данные GigaChat

Получите `CLIENT_ID` и `CLIENT_SECRET` в личном кабинете разработчика Сбера.

### 2. Настройте переменные окружения

Создайте файл `llmapi/.env`:

```env
USE_GIGACHAT=true
GIGACHAT_CLIENT_ID=ваш_client_id
GIGACHAT_CLIENT_SECRET=ваш_client_secret
```

### 3. Настройте ChatAPI

Создайте файл `chatapi/.env` (если его нет):

```env
LLM_API_URL=http://localhost:8002
CONNECTION_STRING=sqlite:///database.db
```

### 4. Установите зависимости

```bash
# В папке llmapi
pip install -r requirements.txt

# В папке chatapi
pip install -r requirements.txt
```

### 5. Запустите сервисы

```bash
# Терминал 1: LLM API
cd llmapi
python -m uvicorn main:app --reload --port 8002

# Терминал 2: Chat API
cd chatapi
python -m uvicorn main:app --reload --port 8001
```

## Проверка работы

1. Создайте чат через веб-интерфейс
2. Отправьте сообщение в чат с LLM-ботом
3. Дождитесь ответа от GigaChat API

## Переключение между режимами

### Использование GigaChat API:
```env
USE_GIGACHAT=true
```

### Использование локальной модели:
```env
USE_GIGACHAT=false
MODEL_PATH=./models/Qwen3-0.6B/
CHECK_CUDA=true
```

## Подробная документация

См. `llmapi/GIGACHAT_GUIDE.md` для подробной документации по работе с GigaChat API.

