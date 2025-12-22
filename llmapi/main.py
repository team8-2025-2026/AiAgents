from gigachat import GigaChat
from fastapi import FastAPI
from dataclasses import dataclass
from typing import Optional, List
from pydantic import BaseModel
from contextlib import asynccontextmanager
import concurrent.futures
import requests
import os
import re


@dataclass
class AppContext:
    gigachat_client: Optional[GigaChat] = None
    thread_pool: Optional[concurrent.futures.ThreadPoolExecutor] = None


class AskRequestHistoryItem(BaseModel):
    text: str
    author: str


# Environment variables
GIGACHAT_CREDENTIALS = os.getenv('GIGACHAT_CREDENTIALS')  # Путь к файлу с credentials или сам credentials
GIGACHAT_AUTH_TOKEN = os.getenv('GIGACHAT_AUTH_TOKEN')  # Альтернативный способ - прямой токен
GIGACHAT_SCOPE = os.getenv('GIGACHAT_SCOPE', 'GIGACHAT_API_PERS')  # Scope для авторизации
CHAT_API = os.getenv('CHAT_API')
LLM_CHAT_TOKEN = os.getenv('LLM_CHAT_TOKEN')


# Constants
SEND_MESSAGE_ATTEMPTS = 5


def clean_markdown(text: str) -> str:
    """
    Удаляет markdown форматирование из текста
    """
    if not text:
        return text
    
    # Удаляем заголовки (# ## ###)
    text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
    
    # Удаляем жирный и курсив (**text**, *text*)
    text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)  # **text** -> text
    text = re.sub(r'\*([^*]+)\*', r'\1', text)  # *text* -> text
    text = re.sub(r'__([^_]+)__', r'\1', text)  # __text__ -> text
    text = re.sub(r'_([^_]+)_', r'\1', text)  # _text_ -> text
    
    # Удаляем inline код (`code`)
    text = re.sub(r'`([^`]+)`', r'\1', text)
    
    # Удаляем блоки кода (```code```)
    text = re.sub(r'```[\s\S]*?```', '', text)
    
    # Удаляем математические формулы ($...$ и $$...$$)
    text = re.sub(r'\$\$[\s\S]*?\$\$', '', text)  # Блоки формул
    text = re.sub(r'\$([^$]+)\$', r'\1', text)  # Inline формулы
    
    # Удаляем ссылки [text](url) -> text
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
    
    # Удаляем маркеры списков (-, *, +, цифры.)
    text = re.sub(r'^[\s]*[-*+]\s+', '', text, flags=re.MULTILINE)
    text = re.sub(r'^[\s]*\d+\.\s+', '', text, flags=re.MULTILINE)
    
    # Удаляем горизонтальные линии (---, ***)
    text = re.sub(r'^[-*]{3,}$', '', text, flags=re.MULTILINE)
    
    # Удаляем лишние пустые строки (более 2 подряд)
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    # Убираем пробелы в начале и конце
    text = text.strip()
    
    return text


# Промпт с контекстом образовательной платформы
EDUCATIONAL_PLATFORM_PROMPT = (
    "Привет! Ты AI-ассистент на образовательной платформе. "
    "Твоя задача - помогать ученикам в обучении, отвечать на их вопросы, "
    "объяснять сложные темы простым языком и поддерживать их в учебном процессе. "
    "Будь дружелюбным, терпеливым и профессиональным. "
    "КРИТИЧЕСКИ ВАЖНО: Отвечай ТОЛЬКО простым текстом, БЕЗ ЛЮБЫХ символов markdown форматирования. "
    "ЗАПРЕЩЕНО использовать: # ## ### (заголовки), $ $$ (формулы), ** * (жирный/курсив), ` (код), []() (ссылки), - * (списки). "
    "Используй ТОЛЬКО обычный текст, пробелы и переносы строк. "
    "Математические формулы пиши обычным текстом, например: 'D = b в квадрате минус 4ac' вместо 'D = b^2 - 4ac'. "
    "Вот вопрос ученика:"
)


@asynccontextmanager
async def load_app_context(app: FastAPI):
    # Инициализация GigaChat клиента
    try:
        if GIGACHAT_AUTH_TOKEN and GIGACHAT_AUTH_TOKEN != "your_gigachat_token_here":
            # Используем прямой токен авторизации
            print("Инициализация GigaChat с токеном авторизации...")
            context.gigachat_client = GigaChat(
                credentials=GIGACHAT_AUTH_TOKEN,
                scope=GIGACHAT_SCOPE,
                verify_ssl_certs=False
            )
            print("GigaChat клиент успешно инициализирован")
        elif GIGACHAT_CREDENTIALS:
            # Используем credentials из файла или переменной окружения
            print("Инициализация GigaChat с credentials...")
            context.gigachat_client = GigaChat(
                credentials=GIGACHAT_CREDENTIALS,
                scope=GIGACHAT_SCOPE,
                verify_ssl_certs=False
            )
            print("GigaChat клиент успешно инициализирован")
        else:
            print("[WARNING] GigaChat токен не указан или является заглушкой.")
            print("[WARNING] LLM API будет работать, но запросы к GigaChat будут возвращать ошибку.")
            print("[WARNING] Установите переменную окружения GIGACHAT_AUTH_TOKEN с реальным токеном.")
            context.gigachat_client = None
    except Exception as ex:
        print(f"[ERROR] Ошибка инициализации GigaChat: {ex}")
        print("[WARNING] Продолжаем работу без GigaChat клиента")
        context.gigachat_client = None

    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        context.thread_pool = executor

        yield


app =       FastAPI(lifespan=load_app_context)
context =   AppContext()


def process_answer(chat_id: int, history: List[AskRequestHistoryItem]):
    print("Processing answer with GigaChat")
    
    try:
        # Находим последнее сообщение от пользователя
        last_user_message = None
        for item in reversed(history):
            if item.author == "user":
                last_user_message = item.text
                break
        
        if not last_user_message:
            print("[ERROR] Не найдено сообщение от пользователя в истории")
            response = "Не удалось найти вопрос пользователя"
        else:
            # Формируем историю сообщений для GigaChat
            messages = []

            # Добавляем предыдущие сообщения из истории для контекста
            # Ограничиваем историю последними 6 сообщениями для оптимизации скорости
            recent_history = history[-6:] if len(history) > 6 else history
            
            for item in recent_history:
                if item.author == "user" and item.text == last_user_message:
                    # Пропускаем последнее сообщение - добавим его отдельно с промптом
                    continue
                elif item.author == "user":
                    messages.append({
                        "role": "user",
                        "content": item.text
                    })
                elif item.author == "assistant":
                    messages.append({
                        "role": "assistant",
                        "content": item.text
                    })

            # Оборачиваем последнее сообщение пользователя в промпт с контекстом образовательной платформы
            full_query = f"{EDUCATIONAL_PLATFORM_PROMPT} {last_user_message}"
            
            # Добавляем последнее сообщение пользователя с контекстом образовательной платформы
            messages.append({
                "role": "user",
                "content": full_query
            })
            
            # Отправляем запрос в GigaChat
            print(f"Sending request to GigaChat with {len(messages)} messages")
            print(f"Last user message (with context): {full_query[:200]}...")
            
            # Проверяем, что GigaChat клиент инициализирован
            if context.gigachat_client is None:
                raise ValueError("GigaChat клиент не инициализирован. Укажите правильный GIGACHAT_CREDENTIALS в .env файле")
            
            # GigaChat принимает строку, а не список словарей
            # Формируем полный текст запроса с историей
            if len(messages) > 1:
                # Если есть история, объединяем все сообщения
                full_text = ""
                for msg in messages[:-1]:  # Все кроме последнего
                    role = msg.get("role", "user")
                    content = msg.get("content", "")
                    if role == "user":
                        full_text += f"Пользователь: {content}\n"
                    elif role == "assistant":
                        full_text += f"Ассистент: {content}\n"
                # Добавляем последнее сообщение
                full_text += messages[-1].get("content", "")
            else:
                # Если только одно сообщение
                full_text = messages[0].get("content", "") if messages else full_query
            
            # Вызываем GigaChat API со строкой
            print(f"Full text to send (first 300 chars): {full_text[:300]}...")
            try:
                giga_response = context.gigachat_client.chat(full_text)
                print(f"GigaChat response type: {type(giga_response)}")
            except Exception as chat_error:
                print(f"[ERROR] Ошибка при вызове GigaChat: {chat_error}")
                import traceback
                traceback.print_exc()
                raise
            
            # Извлекаем текст ответа из объекта ChatCompletion
            # GigaChat возвращает объект ChatCompletion
            response = None
            try:
                if hasattr(giga_response, 'choices') and giga_response.choices:
                    # Если есть choices, берем первый
                    choice = giga_response.choices[0]
                    if hasattr(choice, 'message'):
                        response = choice.message.content
                    elif hasattr(choice, 'content'):
                        response = choice.content
                    else:
                        response = str(choice)
                elif hasattr(giga_response, 'content'):
                    response = giga_response.content
                elif isinstance(giga_response, str):
                    response = giga_response
                else:
                    # Пытаемся получить ответ через другие атрибуты
                    response = getattr(giga_response, 'message', None)
                    if response and hasattr(response, 'content'):
                        response = response.content
                    else:
                        # Последняя попытка - преобразовать в строку
                        response = str(giga_response)
                
                if not response:
                    print("[ERROR] Ответ от GigaChat пустой!")
                    response = "Не удалось получить ответ от GigaChat"
                else:
                    # Удаляем markdown форматирование из ответа
                    response = clean_markdown(response)
                
                print(f"Got response from GigaChat (cleaned): {response[:100] if response else 'EMPTY'}...")
            except Exception as extract_error:
                print(f"[ERROR] Ошибка при извлечении ответа: {extract_error}")
                import traceback
                traceback.print_exc()
                response = f"Ошибка при обработке ответа: {extract_error}"
        
    except Exception as ex:
        print(f"[ERROR] Ошибка при получении ответа от GigaChat: {ex}")
        import traceback
        traceback.print_exc()
        response = "Произошла ошибка во время попытки ответа, напишите позже."
    
    # Отправляем ответ обратно в Chat API
    for attempt in range(SEND_MESSAGE_ATTEMPTS):
        print(f"Sending response to Chat API (attempt {attempt + 1}/{SEND_MESSAGE_ATTEMPTS})")
        try:
            chat_response = requests.post(
                f"{CHAT_API}/chat/send_message",
                params={
            "id": chat_id,
            "text": response,
            "access_token": LLM_CHAT_TOKEN
                }
            )

            if chat_response.status_code == 200:
                print("Response successfully sent to Chat API")
                break
            else:
                print(f"Chat API returned status code: {chat_response.status_code}")
        except Exception as ex:
            print(f"[ERROR] Ошибка при отправке ответа в Chat API: {ex}")
    
    print("Done")
    


@app.post("/ask")
def ask(chat_id: int, history: List[AskRequestHistoryItem]):
    """
    Запрашивает ответа у LLM.
    Возвращает "success" = True, если сообщение принято в обработку, False - иначе.
    А сам результат ответа LLM-ки возвращается асинхронно, отправляя сообщение в нужный чат с помощью f"{CHAT_API}/chat/send_message"
    """

    context.thread_pool.submit(process_answer, chat_id=chat_id, history=history)
    
    return { "success": True }
