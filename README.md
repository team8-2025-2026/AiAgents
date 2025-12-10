# ИИ агенты для образовательных платформ

Интеллектуальные помощники для обучающих платформ, специализирующиеся на подготовке к ЕГЭ. Система анализирует обращения пользователей, ищет аналогичные кейсы в базе знаний и предлагает готовые решения.

## 🎯 Основные возможности

- **Навигация и поддержка**: помощь с навигацией по сайту, расписанием курсов, связью с преподавателями
- **Умный поиск**: анализ запросов и поиск похожих случаев в документации
- **Проверка тестов**: сверка ответов студентов с правильными решениями
- **Эскалация**: автоматическая передача сложных вопросов консультантам
- **История и аналитика**: отслеживание диалогов и улучшение базы знаний

## 👥 Пользователи

- **Студенты**: проходят курсы подготовки к ЕГЭ/ОГЭ, ищут материалы, задают вопросы
- **Консультанты/преподаватели**: отвечают на сложные вопросы, контролируют качество ответов

## 🚀 Быстрый старт

### Требования

- Python 3.8+
- Node.js 16+
- npm или yarn
- Docker and Docker compose
- LLM models installed

### Установка

#### Install `git xet`

```bash
curl --proto '=https' --tlsv1.2 -sSf https://raw.githubusercontent.com/huggingface/xet-core/refs/heads/main/git_xet/install.sh | sh
```

#### Check installation

```bash
git xet --version
```

#### Clone model repository

Это может занять некоторое объёмное время.
Я рекомендую взять `Qwen3-1.7B`, но если прямо не тянет компьютер, то `Qwen3-0.6B`.

##### Qwen3-0.6B: весит 1.5GB

```bash
export MODEL_REPOSITORY="https://huggingface.co/Qwen/Qwen3-0.6B"
```

##### Qwen3-1.7B: весит 4GB

```bash
export MODEL_REPOSITORY="https://huggingface.co/Qwen/Qwen3-1.7B"
```

##### Qwen3-4B: весит 8GB:

```bash
export MODEL_REPOSITORY="git clone https://huggingface.co/Qwen/Qwen3-4B"
```

##### YandexGPT-5-Lite-8B-pretrain: весит 30GB:

```bash
export MODEL_REPOSITORY="git clone https://huggingface.co/yandex/YandexGPT-5-Lite-8B-pretrain"
```

#### Загрузка модели

```bash
cd llmapi/; mkdir models/ ; cd models/
git clone $MODEL_REPOSITORY
cd ../
```

### Настройка переменных окружения

Заполнить [.env](.env) файл. Пример файла?

```Properties
CONNECTION_STRING=sqlite:///database.db
ADMIN_ACCESS_TOKEN=FHj0osc0461Yc7KT4Hpgbg91f326OtGpghHBS6qiCKTBlJjg6L
LLM_CHAT_TOKEN=V0MP0Pd82FQ0FWkSl9AXsCWetxsrekijGACCRLD9XDOG1zVrba
MODEL_PATH=./models/Qwen3-0.6B
CHECK_CUDA=true
CHAT_API=http://127.0.0.1:8001
```

### Запуск

Запускает докер контейнеры для всех апи (и клиента в том числе).
При первом запуске будет очень долго, потому что создаются докер образы.

```bash
docker compose up
```

#### Запуск в даемоне

```bash
docker compose up -d
```

#### Остановка (при запуске в даемоне)

```bash
docker compose down
```

## 📁 Структура проекта

```
.
├── authapi/          # API для аутентификации и управления пользователями
│   └── main.py      # FastAPI приложение
├── webui/           # React веб-интерфейс
│   ├── src/
│   │   ├── api/     # API клиенты
│   │   ├── components/  # React компоненты
│   │   ├── pages/   # Страницы приложения
│   │   └── styles/  # CSS стили
│   └── package.json
└── README.md
```

## 📋 Документация

- [Техническое задание](./TERMS.md) - подробное описание требований, функциональности и архитектуры проекта
- [WebUI README](./webui/README.md) - документация по веб-интерфейсу
- [Инструкция по регистрации и входу](./USER_GUIDE.md) - пошаговый гайд для пользователей
