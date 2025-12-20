from transformers import AutoModelForCausalLM, AutoTokenizer
from fastapi import FastAPI
from dataclasses import dataclass
from typing import Optional, List
from pydantic import BaseModel
from contextlib import asynccontextmanager
import dotenv
import torch
import os
from gigachat_client import GigaChatClient, create_gigachat_client_from_env


@dataclass
class AppContext:
    model: Optional[AutoModelForCausalLM]
    tokenizer: Optional[AutoTokenizer]
    gigachat_client: Optional[GigaChatClient]
    use_gigachat: bool = False


class AskRequestHistoryItem(BaseModel):
    text: str
    author: str


@asynccontextmanager
async def load_app_context(app: FastAPI):
    dotenv.load_dotenv()
    
    # Проверяем, используется ли GigaChat API
    use_gigachat = os.getenv('USE_GIGACHAT', 'false').lower() == 'true'
    
    if use_gigachat:
        print("Используется GigaChat API")
        gigachat_client = create_gigachat_client_from_env()
        if gigachat_client is None:
            raise ValueError(
                "USE_GIGACHAT=true, но не заданы GIGACHAT_CLIENT_ID и GIGACHAT_CLIENT_SECRET. "
                "Пожалуйста, задайте эти переменные в .env файле."
            )
        context.gigachat_client = gigachat_client
        context.use_gigachat = True
        context.model = None
        context.tokenizer = None
        print("GigaChat клиент успешно инициализирован")
    else:
        print("Используется локальная модель")
        model_path = os.getenv('MODEL_PATH')
        if not model_path:
            raise ValueError("MODEL_PATH не задан в .env файле")
        
        check_cuda = os.getenv('CHECK_CUDA') == 'true'
        context.tokenizer = AutoTokenizer.from_pretrained(model_path)
        
        if check_cuda and torch.cuda.is_available():
            print("CUDA is available. Loading model on GPU.")
            context.model = AutoModelForCausalLM.from_pretrained(model_path).cuda()
        else:
            print("CUDA is not available. Loading model on CPU.")
            context.model = AutoModelForCausalLM.from_pretrained(model_path)
        
        context.gigachat_client = None
        context.use_gigachat = False

    yield

app =       FastAPI(lifespan=load_app_context)
context =   AppContext(model=None,
                     tokenizer=None,
                     gigachat_client=None,
                     use_gigachat=False)


@app.post("/ask")
def ask(history: List[AskRequestHistoryItem]):
    messages = []

    for item in history:
        # Преобразуем роли для GigaChat API
        role = item.author.lower()
        if role == "user" or role == "human":
            role = "user"
        elif role == "assistant" or role == "llm":
            role = "assistant"
        else:
            role = "user"  # По умолчанию user
        
        messages.append({
            "role": role,
            "content": item.text
        })

    try:
        if context.use_gigachat and context.gigachat_client:
            # Используем GigaChat API
            max_tokens = int(os.getenv('GIGACHAT_MAX_TOKENS', '512'))
            temperature = float(os.getenv('GIGACHAT_TEMPERATURE', '0.7'))
            model = os.getenv('GIGACHAT_MODEL', 'GigaChat')
            
            response_data = context.gigachat_client.chat_completion(
                messages=messages,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            # Извлекаем текст ответа из ответа GigaChat API
            if 'choices' in response_data and len(response_data['choices']) > 0:
                response = response_data['choices'][0]['message']['content']
            else:
                raise Exception("Неожиданный формат ответа от GigaChat API")
        else:
            # Используем локальную модель
            if context.model is None or context.tokenizer is None:
                raise Exception("Локальная модель не загружена")
            
            text = context.tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True
            )
            
            inputs = context.tokenizer(text, return_tensors="pt").to(context.model.device)
            response_ids = context.model.generate(**inputs, max_new_tokens=32768)[0][len(inputs.input_ids[0]):].tolist()
            response = context.tokenizer.decode(response_ids, skip_special_tokens=True)
    except Exception as ex:
        return {
            "success": False,
            "error": "Неопределённая ошибка во время выполнения: " + str(ex)
        }
    
    return {
        "success": True,
        "data": {
            "text": response
        }
    }
