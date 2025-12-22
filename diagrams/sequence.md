# Диаграммы последовательностей проекта

## Сценарий 1: Авторизация пользователя

```mermaid
sequenceDiagram
    participant U as Пользователь
    participant W as WebUI
    participant A as Auth API
    participant DB as База данных

    U->>W: Ввод email и пароля
    W->>A: POST /user?email=...&password=...
    A->>DB: Проверка пользователя
    DB-->>A: Данные пользователя
    A->>A: Проверка пароля (bcrypt)
    alt Пароль верный
        A-->>W: access_token, данные пользователя
        W->>W: Сохранение токена в localStorage
        W-->>U: Перенаправление на главную страницу
    else Пароль неверный
        A-->>W: Ошибка 401
        W-->>U: Сообщение об ошибке
    end
```

## Сценарий 2: Создание нового чата

```mermaid
sequenceDiagram
    participant U as Пользователь
    participant W as WebUI
    participant C as Chat API
    participant DB as База данных

    U->>W: Нажатие "Создать чат"
    W->>W: Получение access_token из localStorage
    W->>C: PUT /chat?access_token=...
    C->>DB: Проверка пользователя по токену
    DB-->>C: Данные пользователя
    alt Пользователь найден и статус STUDENT
        C->>DB: Создание нового чата (companion_type=LLM)
        DB-->>C: ID созданного чата
        C-->>W: Данные чата
        W-->>U: Отображение нового чата в списке
    else Ошибка
        C-->>W: Ошибка
        W-->>U: Сообщение об ошибке
    end
```

## Сценарий 3: Отправка сообщения и получение ответа от LLM

```mermaid
sequenceDiagram
    participant U as Пользователь
    participant W as WebUI
    participant C as Chat API
    participant L as LLM API
    participant G as GigaChat
    participant DB as База данных

    U->>W: Ввод сообщения и отправка
    W->>C: POST /chat/send_message?id=...&text=...&access_token=...
    C->>DB: Проверка токена и сохранение сообщения пользователя
    DB-->>C: Сообщение сохранено
    
    C->>DB: Получение истории сообщений (последние 10)
    DB-->>C: История сообщений
    
    C->>L: POST /ask?chat_id=... (история сообщений)
    L-->>C: {success: true} (асинхронная обработка)
    
    Note over L: Асинхронная обработка
    L->>L: Формирование запроса с историей
    L->>G: Вызов GigaChat API
    G-->>L: Ответ от LLM
    L->>L: Очистка markdown форматирования
    
    L->>C: POST /chat/send_message?id=...&text=...&access_token=LLM_TOKEN
    C->>DB: Сохранение ответа LLM
    DB-->>C: Сообщение сохранено
    C-->>L: Подтверждение
    
    Note over W: Polling или WebSocket для обновления
    W->>C: GET /chat/history?id=...&access_token=...
    C->>DB: Получение всех сообщений чата
    DB-->>C: Список сообщений
    C-->>W: История с новым ответом
    W-->>U: Отображение ответа LLM
```

## Сценарий 4: Эскалация чата к учителю

```mermaid
sequenceDiagram
    participant U as Пользователь
    participant W as WebUI
    participant C as Chat API
    participant DB as База данных
    participant T as Учитель

    Note over C: После каждого запроса к LLM
    C->>C: Увеличение счетчика llm_requests_count
    
    alt llm_requests_count >= 3 (ESCALATION_THRESHOLD)
        C->>DB: Поиск доступного учителя
        DB-->>C: Данные учителя
        C->>DB: Обновление чата (companion_type=HUMAN, companion_id=teacher_id)
        DB-->>C: Чат обновлен
        
        C->>DB: Создание системного сообщения об эскалации
        DB-->>C: Сообщение создано
        
        Note over T: Учитель видит чат в списке
        T->>W: Открытие чата
        W->>C: GET /chats?access_token=...
        C->>DB: Получение чатов учителя
        DB-->>C: Список чатов (включая эскалированный)
        C-->>W: Список чатов
        W-->>T: Отображение эскалированного чата
    end
```

## Сценарий 5: Получение списка чатов

```mermaid
sequenceDiagram
    participant U as Пользователь
    participant W as WebUI
    participant C as Chat API
    participant DB as База данных

    U->>W: Открытие страницы с чатами
    W->>W: Получение access_token из localStorage
    W->>C: GET /chats?access_token=...
    C->>DB: Проверка пользователя по токену
    DB-->>C: Данные пользователя
    
    alt Пользователь найден
        C->>DB: Получение чатов пользователя
        DB-->>C: Список чатов
        C-->>W: Массив чатов с метаданными
        W->>W: Обработка и форматирование данных
        W-->>U: Отображение списка чатов
    else Пользователь не найден
        C-->>W: Ошибка 401
        W-->>U: Перенаправление на страницу входа
    end
```

