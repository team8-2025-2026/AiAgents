# Спринт 6

## Скрам

???

## Цель

Делаем демо приложения

## Задачи

### То, что нужно доделать с прошлых спринтов:

* Добавить в репозиторий [Диаграмму активности](https://img.plantuml.biz/plantuml/svg/xLR1Qjj04BqBz0zpj6aWT_lGzD9JAVJG3mXK8GOt3R5AhxAKkYqn5Yc1G20j_O22ubgn8aNsB-p-Gh-aRsObMQwLGaakXHv2TaUpRzwyULfhP-3k7hblN_Tjo-svVOVKXSfKf8Twg19zh1ALOZV2EYGrLv5QQayjy72XfgIM-9VfCHvWYpnVnTY7jcLRWikB8-VGsSMgexusPeyDxWo1K-qJdYpA8bq-zKLsCHAG3Hu-Je1U88jwjegezVpPIzecYKHubd0lxIxJwErHIrqMqHzbJu_RvEux1tY4-ctR8Z8q4y2b97Kp_86joi4troVwFLVtfK2El17NIt4anv4bSbFaeRykWrL5RuG-ZZTYgjY4vpfWGH24EFfaarn93pDXqOmM3IUf9MGIcLEwHOM4KsHCjfZ_44Kpm2JjRXstLDAeZEM8MQEbe5CCcsiXik2kS_1UZnPWqlQTqvv9m9pActfaDkVeCDKUzFPBXnJawATt9YEGLWCzx8W4-gDGBIaG3TmtXsRjz0SE2e2kzcibllECWPkj38wHGp6UBlISyNovzoR8WrUzFLusO1loit8y0Vj1Vy2SGptHdm1visRRkzwYYPGj2jaM5n9TBzXhh0sN5FVyXhTDJv-y-BEn-Tsz4W_599CJBmD8pgwiUyQ0HcdJ0mRFW5YOLu61JjLvirC_Wrif0wiAbg1CZse6r07RA2BcLTM0wFzT-O-vyXBKheq_fkfM6g_45Lc0tT26YfgC-WqbvokklcIoTMIyaN4io9S_1fketPNZwtSb4nHs7coahlWIH--nNEGGEk7eDH3OuZ4I5-obgToTjvnGcNYjmeFuyvxklBytInirUkTlNLc1rOqYluK9cF4dHGWFYfQUiCZDJQF7XGKUpAmL0_CTGk_sUtsdPjZ8Y6i6mZueD1UBXPkr8p4AjiS8U_18zILXMpie9fzIjlKB)
* Сделать Диаграмму классов (domain model)
* Сделать Диаграмму последовательностей (Sequence)
* Архитектуру проектов?
* Создать и отметить задачи, которые мы выполняли в течение начала семестра

### То, что нужно сделать за этот спринт

#### Пофиксить базу данных

В данный момент в AuthAPI база данных подключается по строке `sqlite:///database.db`, что создает файл в локальной папке сервиса, что не хорошо, потому что эту базу данных мы хотим использовать и в других сервисах.
Вывести её в отдельный сервис.

#### Chat API

Хотим реализовать чат Student-(Teacher/Assistent/LLM), с возможностью смены собеседника (с одной стороны) а так же если чат происходит с LLM-кой, то все сообщения пользователя переадресуются в LLM API, а ответы LLM-ки возвращаются как сообщения.

##### **GET** `/chat`

Возвращает информацию о чате

###### Request

```json
{
    "id": 123,
    "access_token": "..."
}
```

###### Response

```json
{
    "success": true,
    "error": "...",
    "data": {
        "id": 123,
        "title": "...",
        "companion": {
            "type": "HUMAN/LLM",
            "data": { // in case of "HUMAN" type
                "id": 123,
                "first_name": "...",
                "last_name": "...",
                "status": "...",
                "description": "...",
            },
            "data": { // in case of "LLM" type
                "name": "...",
                "description": "...",
            }
        }
    }
}
```

##### **PUT** `/chat`

Создает чат. По умолчанию чат создается с чат ботом.

###### Request

```json
{
    "access_token": "..."
}
```

###### Response

```json
{
    "success": true,
    "error": "...",
    "data": {
        "id": 123,
        "title": "...",
        "companion": {
            "type": "HUMAN/LLM",
            "data": { // in case of "HUMAN" type
                "id": 123,
                "first_name": "...",
                "last_name": "...",
                "status": "...",
                "description": "...",
            },
            "data": { // in case of "LLM" type
                "name": "...",
                "description": "...",
            }
        }
    }
}
```

##### **PUT** `/chat`

Создает чат. По умолчанию чат создается с чат ботом. Создать чат может только студент.

###### Request

```json
{
    "access_token": "..."
}
```

###### Response

```json
{
    "success": true,
    "error": "...",
    "data": {
        "id": 123,
        "title": "...",
        "companion": {
            "type": "HUMAN/LLM",
            "data": { // in case of "HUMAN" type
                "id": 123,
                "first_name": "...",
                "last_name": "...",
                "status": "...",
                "description": "...",
            },
            "data": { // in case of "LLM" type
                "name": "...",
                "description": "...",
            }
        }
    }
}
```

##### **UPDATE** `/chat`

Обновляет чат. `title` для каждого собеседника свой, то есть если пользователь поменял название,
то только у самого пользователя оно поменяется, а у собеседника - нет.

###### Request

```json
{
    "title": "...",
    "access_token": "..."
}
```

###### Response

```json
{
    "success": true,
    "error": "...",
    "data": {
        "id": 123,
        "title": "...",
        "companion": {
            "type": "HUMAN/LLM",
            "data": { // in case of "HUMAN" type
                "id": 123,
                "first_name": "...",
                "last_name": "...",
                "status": "...",
                "description": "...",
            },
            "data": { // in case of "LLM" type
                "name": "...",
                "description": "...",
            }
        }
    }
}
```

##### **DELETE** `/chat`

Удаляет чат. Удалить чат может только студент.

###### Request

```json
{
    "id": 123,
    "access_token": "..."
}
```

###### Response

```json
{
    "success": true,
    "error": "...",
    "data": {
        "id": 123,
        "title": "...",
        "companion": {
            "type": "HUMAN/LLM",
            "data": { // in case of "HUMAN" type
                "id": 123,
                "first_name": "...",
                "last_name": "...",
                "status": "...",
                "description": "...",
            },
            "data": { // in case of "LLM" type
                "name": "...",
                "description": "...",
            }
        }
    }
}
```

##### **POST** `/chat/send_message`

Отправляет сообщение.

###### Request

```json
{
    "id": 123,
    "text": "...",
    "access_token": "..."
}
```

###### Response

```json
{
    "success": true,
    "error": "...",
    "data": {
        "id": 123,
        "chat_id": 123,
        "text": "...",
        "author": {
            "type": "HUMAN/LLM",
            "data": { // in case of "HUMAN" type
                "id": 123,
                "first_name": "...",
                "last_name": "...",
                "status": "...",
                "description": "...",
            },
            "data": { // in case of "LLM" type
                "name": "...",
                "description": "...",
            }
        }
    }
}
```

##### **GET** `/chat/history`

Загружает историю чата. (По-хорошему, нужно добавить пагинацию, но это сделаем потом)

###### Request

```json
{
    "id": 123,
    "access_token": "..."
}
```

###### Response

```json
{
    "success": true,
    "error": "...",
    "data": [
        "id": 123,
        "chat_id": 123,
        "text": "...",
        "author": {
            "type": "HUMAN/LLM",
            "data": { // in case of "HUMAN" type
                "id": 123,
                "first_name": "...",
                "last_name": "...",
                "status": "...",
                "description": "...",
            },
            "data": { // in case of "LLM" type
                "name": "...",
                "description": "...",
            }
        },
        // ...
    ]
}
```

##### **GET** `/chats`

Загружает все чаты пользователя.

###### Request

```json
{
    "access_token": "..."
}
```

###### Response

```json
{
    "success": true,
    "error": "...",
    "data": [
        "id": 123,
        "title": "...",
        "companion": {
            "type": "HUMAN/LLM",
            "data": { // in case of "HUMAN" type
                "id": 123,
                "first_name": "...",
                "last_name": "...",
                "status": "...",
                "description": "...",
            },
            "data": { // in case of "LLM" type
                "name": "...",
                "description": "...",
            }
        },
        // ...
    ]
}
```

#### UI для взаимодействия с чатом

* Создание чата
* Удаление чата
* Переименование чата
* Загрузка сообщений
* Отправление сообщений

#### Заглушка для LLM API

Приватный сервис, у которого не будет выходов в внешнюю сеть. То есть к этому сервису смогут подключаться только наши сервисы по типу Auth API и Chat API

##### **POST** `/ask`

Отправляет запрос LLM-ке.

###### Request

```json
{
    "history": [
        "text": "...",
        "author": "..."
        // ...
    ]
}
```

###### Response

```json
{
    "success": true,
    "error": "...",
    "data": {
        "text": "...",
    }
}
```

#### Docker Swarm

Обернуть все наши API-шки Docker контейнерами и настроить запуск с помощью Docker Swarm

#### Написать unit тесты

По необходимости

#### Добавить CI/CD

Добавить автоматическое тестирование кода
