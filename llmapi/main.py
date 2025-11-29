from transformers import AutoModelForCausalLM, AutoTokenizer
from fastapi import FastAPI
from dataclasses import dataclass
from typing import Optional, List
from pydantic import BaseModel
from contextlib import asynccontextmanager
import concurrent.futures
import requests
import dotenv
import torch
import os


@dataclass
class AppContext:
    model: Optional[AutoModelForCausalLM] = None
    tokenizer: Optional[AutoTokenizer] = None
    thread_pool: Optional[concurrent.futures.ThreadPoolExecutor] = None


class AskRequestHistoryItem(BaseModel):
    text: str
    author: str


# Enviroment variables
dotenv.load_dotenv()
MODEL_PATH = os.getenv('MODEL_PATH')
CHECK_CUDA = os.getenv('CHECK_CUDA')
CHAT_API = os.getenv('CHAT_API')
LLM_CHAT_TOKEN = os.getenv('LLM_CHAT_TOKEN')


# Constants
SEND_MESSAGE_ATTEMPTS = 5


@asynccontextmanager
async def load_app_context(app: FastAPI):
    model_path = MODEL_PATH
    check_cuda = CHECK_CUDA == 'true'
    context.tokenizer = AutoTokenizer.from_pretrained(model_path)
    
    if check_cuda and torch.cuda.is_available():
        print("CUDA is available. Loading model on GPU.")
        context.model = AutoModelForCausalLM.from_pretrained(model_path).cuda()
    else:
        print("CUDA is not available. Loading model on CPU.")
        context.model = AutoModelForCausalLM.from_pretrained(model_path)

    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        context.thread_pool = executor

        yield

app =       FastAPI(lifespan=load_app_context)
context =   AppContext()


def process_answer(chat_id: int, history: List[AskRequestHistoryItem]):
    messages = []

    for item in history:
        messages.append({
            "role": item.author,
            "content": item.text
        })

    try:
        text = context.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True
        )
        
        inputs = context.tokenizer(text, return_tensors="pt").to(context.model.device)
        response_ids = context.model.generate(**inputs, max_new_tokens=32768)[0][len(inputs.input_ids[0]):].tolist()
        response = context.tokenizer.decode(response_ids, skip_special_tokens=True)
    except Exception as ex:
        print("[ERROR]", ex)

        response = "Северная ошибка произошла во время попытки ответа, напишите позже."
    
    for _ in range(SEND_MESSAGE_ATTEMPTS):
        response = requests.post(f"{CHAT_API}/chat/send_message", params={
            "id": chat_id,
            "text": response,
            "access_token": LLM_CHAT_TOKEN
        })

        if response.status_code == 200:
            break


@app.post("/ask")
def ask(chat_id: int, history: List[AskRequestHistoryItem]):
    """
    Запрашивает ответа у LLM.
    Возвращает "success" = True, если сообщение принято в обработку, False - иначе.
    А сам результат ответа LLM-ки возвращается асинхронно, отправляя сообщение в нужный чат с помощью f"{CHAT_API}/chat/send_message"
    """

    context.thread_pool.submit(process_answer, chat_id=chat_id, history=history)
    
    return { "success": True }
