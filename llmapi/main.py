from transformers import AutoModelForCausalLM, AutoTokenizer
from fastapi import FastAPI
from dataclasses import dataclass
from typing import Optional, List
from pydantic import BaseModel
from contextlib import asynccontextmanager
import dotenv
import torch
import os


@dataclass
class AppContext:
    model: Optional[AutoModelForCausalLM]
    tokenizer: Optional[AutoTokenizer]


class AskRequestHistoryItem(BaseModel):
    text: str
    author: str


@asynccontextmanager
async def load_app_context(app: FastAPI):
    dotenv.load_dotenv()
    model_path = os.getenv('MODEL_PATH')
    check_cuda = os.getenv('CHECK_CUDA') == 'true'
    context.tokenizer = AutoTokenizer.from_pretrained(model_path)
    
    if check_cuda and torch.cuda.is_available():
        print("CUDA is available. Loading model on GPU.")
        context.model = AutoModelForCausalLM.from_pretrained(model_path).cuda()
    else:
        print("CUDA is not available. Loading model on CPU.")
        context.model = AutoModelForCausalLM.from_pretrained(model_path)

    yield

app =       FastAPI(lifespan=load_app_context)
context =   AppContext(model=None,
                     tokenizer=None)


@app.post("/ask")
def ask(history: List[AskRequestHistoryItem]):
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
