# Руководство по работе с GigaChat API

Это руководство описывает, как настроить и использовать GigaChat API в проекте.

## Что такое GigaChat?

GigaChat — это языковая модель от Сбера, предоставляемая через REST API. Она позволяет генерировать текстовые ответы на основе контекста диалога.

## Настройка

### 1. Получение учетных данных

Для работы с GigaChat API необходимо получить:
- **Client ID** — идентификатор клиента
- **Client Secret** — секретный ключ клиента

Эти данные можно получить в личном кабинете разработчика Сбера.

### 2. Настройка переменных окружения

Создайте файл `.env` в папке `llmapi/` со следующим содержимым:

```env
# Включить использование GigaChat API
USE_GIGACHAT=true

# Учетные данные GigaChat
GIGACHAT_CLIENT_ID=your_client_id_here
GIGACHAT_CLIENT_SECRET=your_client_secret_here

# Опционально: Scope для доступа (по умолчанию GIGACHAT_API_PERS)
GIGACHAT_SCOPE=GIGACHAT_API_PERS

# Опционально: Параметры генерации
GIGACHAT_MODEL=GigaChat
GIGACHAT_MAX_TOKENS=512
GIGACHAT_TEMPERATURE=0.7
```

### 3. Установка зависимостей

Убедитесь, что установлены все необходимые зависимости:

```bash
cd llmapi
pip install -r requirements.txt
```

## Использование

### Режимы работы

LLM API поддерживает два режима работы:

1. **Локальная модель** (по умолчанию) — использует локально загруженную модель через transformers
2. **GigaChat API** — использует облачный API GigaChat

Режим выбирается через переменную окружения `USE_GIGACHAT`.

### Переключение между режимами

#### Использование GigaChat API:

```env
USE_GIGACHAT=true
GIGACHAT_CLIENT_ID=your_client_id
GIGACHAT_CLIENT_SECRET=your_client_secret
```

#### Использование локальной модели:

```env
USE_GIGACHAT=false
MODEL_PATH=./models/Qwen3-0.6B/
CHECK_CUDA=true
```

## API Endpoints

### POST /ask

Отправляет запрос на генерацию ответа.

**Request Body:**
```json
[
  {
    "text": "Привет!",
    "author": "user"
  },
  {
    "text": "Привет! Как дела?",
    "author": "assistant"
  },
  {
    "text": "Отлично, спасибо!",
    "author": "user"
  }
]
```

**Response:**
```json
{
  "success": true,
  "data": {
    "text": "Рад слышать! Чем могу помочь?"
  }
}
```

**Ошибка:**
```json
{
  "success": false,
  "error": "Описание ошибки"
}
```

## Параметры GigaChat API

### Модели

Доступные модели можно получить через метод `get_models()` клиента. По умолчанию используется модель `GigaChat`.

### Параметры генерации

- **temperature** (0.0-1.0) — контролирует случайность ответов. Чем выше, тем более креативные ответы. По умолчанию: 0.7
- **max_tokens** — максимальное количество токенов в ответе. По умолчанию: 512

Эти параметры можно настроить через переменные окружения:
- `GIGACHAT_TEMPERATURE`
- `GIGACHAT_MAX_TOKENS`

## Интеграция с ChatAPI

ChatAPI автоматически использует LLM API для генерации ответов в чатах с LLM-ботом. 

Убедитесь, что в `chatapi/.env` указан правильный URL LLM API:

```env
LLM_API_URL=http://localhost:8002
```

## Примеры использования

### Прямое использование клиента

```python
from gigachat_client import GigaChatConfig, GigaChatClient

config = GigaChatConfig(
    client_id="your_client_id",
    client_secret="your_client_secret"
)

client = GigaChatClient(config)

messages = [
    {"role": "user", "content": "Привет!"}
]

response = client.chat_completion(
    messages=messages,
    temperature=0.7,
    max_tokens=512
)

print(response['choices'][0]['message']['content'])
```

### Использование через переменные окружения

```python
from gigachat_client import create_gigachat_client_from_env

client = create_gigachat_client_from_env()

if client:
    messages = [{"role": "user", "content": "Привет!"}]
    response = client.chat_completion(messages=messages)
    print(response['choices'][0]['message']['content'])
```

## Обработка ошибок

Клиент GigaChat автоматически обрабатывает:
- Обновление токенов доступа при истечении
- Повторные попытки при временных ошибках сети
- Валидацию ответов от API

При возникновении ошибок клиент выбрасывает исключение с описанием проблемы.

## Безопасность

⚠️ **Важно:**
- Никогда не коммитьте файлы `.env` с учетными данными в репозиторий
- Храните `GIGACHAT_CLIENT_SECRET` в безопасном месте
- Используйте переменные окружения для хранения секретов
- В продакшене используйте системы управления секретами (например, HashiCorp Vault, AWS Secrets Manager)

## Troubleshooting

### Ошибка "Ошибка получения токена доступа"

- Проверьте правильность `GIGACHAT_CLIENT_ID` и `GIGACHAT_CLIENT_SECRET`
- Убедитесь, что у вас есть доступ к интернету
- Проверьте, что сертификаты SSL установлены корректно

### Ошибка "Неожиданный формат ответа от GigaChat API"

- Проверьте версию API
- Убедитесь, что используете актуальную версию клиента

### Медленные ответы

- Уменьшите `GIGACHAT_MAX_TOKENS` для более быстрых ответов
- Проверьте скорость интернет-соединения
- Рассмотрите использование локальной модели для офлайн-работы

## Дополнительные ресурсы

- [Официальная документация GigaChat API](https://developers.sber.ru/docs/ru/gigachat/api/overview)
- [Документация по аутентификации](https://developers.sber.ru/docs/ru/gigachat/api/authentication)

