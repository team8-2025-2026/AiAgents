from __future__ import annotations

from typing import Optional, Union
from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Field, Session, SQLModel, create_engine, select
from dataclasses import dataclass
from pathlib import Path
import bcrypt
import random
import string
import time
import os
import re
import threading
import requests
import json


# Companion.type
HUMAN = "HUMAN"
LLM = "LLM"
STATUSES = [HUMAN, LLM]


# User.status
STUDENT = "STUDENT"
ASSISTENT = "ASSISTENT"
STATUSES = [STUDENT, ASSISTENT]


# LLM name and descrption
LLM_NAME = "Бот Ассистент"
LLM_DESCRIPION = "Я - учебный бот ассистент, " \
    "помогаю облегчить работу нашей тех поддержке, " \
    "отвечая на стандартные вопросы вместо них."


# Message constants
MAX_MESSAGE_LENGTH = 1024
HISTORY_SIZE = 10


# Environment variables
CONNECTION_STRING = os.getenv('CONNECTION_STRING')
LLM_CHAT_TOKEN = os.getenv('LLM_CHAT_TOKEN')
LLM_API = os.getenv('LLM_API')
AUTH_API = os.getenv('AUTH_API')


class User(SQLModel, table=True):
    id: Optional[int]   = Field(default=None, primary_key=True)
    email: str          = Field(unique=True, index=True)
    first_name: str     = Field()
    last_name: str      = Field()
    status: str         = Field()
    description: str    = Field(default="")
    password_hash: str  = Field()
    access_token: str   = Field(unique=True, index=True)

    def to_json(self) -> dict:
        return {
            "id": self.id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "status": self.status,
            "description": self.description,
        }
    

@dataclass
class ChatCompanion:
    companion_type: str
    user: Optional[User]

    def _llm_data(self) -> dict:
        return {
            "name": LLM_NAME,
            "description": LLM_DESCRIPION
        }

    def to_json(self) -> dict:
        return {
            "type": self.companion_type,
            "data": self.user.to_json() if self.companion_type == HUMAN else self._llm_data(),
        }


class Chat(SQLModel, table=True):
    id: Optional[int]           = Field(default=None, primary_key=True)
    student_title: str          = Field()
    assistent_title: str        = Field()
    companion_type: str         = Field()
    student_id: int             = Field()
    companion_id: Optional[int] = Field(nullable=True)

    def to_json(self, student_data: dict, assistent_companion_data: Optional[dict]) -> dict:
        return {
            "id": self.id,
            "student_title": self.student_title,
            "assistent_title": self.assistent_title,
            "student": student_data,
            "assistent": assistent_companion_data
        }


class Message(SQLModel, table=True):
    id: Optional[int]           = Field(default=None, primary_key=True)
    text: str                   = Field()
    chat_id: int                = Field()
    author_type: str            = Field()  # LLM or HUMAN
    author_id: Optional[int]    = Field(nullable=True)  # Not null if author_type == HUMAN

    def to_json(self, chat_data: dict, author_companion_data: Optional[dict]) -> dict:
        return {
            "id": self.id,
            "text": self.text,
            "chat": chat_data,
            "author_type": self.author_type,
            "author": author_companion_data,
        }


if CONNECTION_STRING is None:
    raise ValueError("CONNECTION_STRING не найден в .env файле. Создайте файл chatapi/.env с CONNECTION_STRING=sqlite:///database.db")

app = FastAPI()
engine = create_engine(CONNECTION_STRING)
SQLModel.metadata.create_all(engine)

# CORS middleware для работы с фронтендом
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В продакшене указать конкретные домены
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


#region Return utils
def error(error: str) -> dict:
    return {
        "success": False,
        "error": error
    }


def success(data: dict) -> dict:
    return {
        "success": True,
        "data": data
    }
#endregion

#region CRUD
@app.get("/chat")
def read_chat(id: int, access_token: str):
    with Session(engine) as session:
        statement = select(Chat).where(Chat.id == id)
        chat = session.exec(statement).first()

        if chat is None:
            return error("Чат не найден")
        else:
            statement = select(User).where(User.id == chat.student_id)
            student_user = session.exec(statement).first()
            if chat.companion_type == HUMAN:
                statement = select(User).where(User.id == chat.companion_id)
                assistent_user = session.exec(statement).first()
            else:
                assistent_user = None
            assistent_companion = ChatCompanion(chat.companion_type, assistent_user)

            if student_user is not None and student_user.access_token == access_token or \
                    assistent_user is not None and assistent_user.access_token == access_token:
                return success( chat.to_json(student_user.to_json(), assistent_companion.to_json()) )
            else:
                return error("Чат не найден")


@app.put("/chat")
def create_chat(access_token: str):
    with Session(engine) as session:
        statement = select(User).where(User.access_token == access_token)
        user = session.exec(statement).first()
        assistent_companion = ChatCompanion(LLM, None)

        if user is None:
            return error("Пользователь не найден")
        elif user.status != STUDENT:
            return error("Чат может создать только пользователь")
        else:
            new_chat = Chat(student_title="Новый чат",
                            assistent_title="Новый чат",
                            companion_type=LLM,
                            companion_id=None,
                            student_id=user.id)
            session.add(new_chat)
            session.commit()

        return success( new_chat.to_json(user.to_json(), assistent_companion.to_json()) )


@app.patch("/chat")
def update_chat(id: int, title: str, access_token: str):
    with Session(engine) as session:
        statement = select(Chat).where(Chat.id == id)
        chat = session.exec(statement).first()

        if chat is None:
            return error("Чат не найден")
        else:
            statement = select(User).where(User.id == chat.student_id)
            student_user = session.exec(statement).first()
            if chat.companion_type == HUMAN:
                statement = select(User).where(User.id == chat.companion_id)
                assistent_user = session.exec(statement).first()
            else:
                assistent_user = None
            assistent_companion = ChatCompanion(chat.companion_type, assistent_user)
            
            if student_user is not None and student_user.access_token == access_token:
                chat.student_title = title
                session.add(chat)
                session.commit()
                session.refresh(chat)

                return success( chat.to_json(student_user.to_json(), assistent_companion.to_json()) )
            elif assistent_user is not None and assistent_user.access_token == access_token:
                chat.assistent_title = title
                session.add(chat)
                session.commit()
                session.refresh(chat)

                return success( chat.to_json(student_user.to_json(), assistent_companion.to_json()) )
            else:
                return error("Чат не найден")


@app.delete("/chat")
def delete_chat(id: int, access_token: str):
    with Session(engine) as session:
        statement = select(Chat).where(Chat.id == id)
        chat = session.exec(statement).first()

        if chat is None:
            return error("Чат не найден")
        else:
            statement = select(User).where(User.id == chat.student_id)
            student_user = session.exec(statement).first()
            if chat.companion_type == HUMAN:
                statement = select(User).where(User.id == chat.companion_id)
                assistent_user = session.exec(statement).first()
            else:
                assistent_user = None
            assistent_companion = ChatCompanion(chat.companion_type, assistent_user)
            
            if student_user is not None and student_user.access_token == access_token:
                session.delete(chat)
                session.commit()

                return success( chat.to_json(student_user.to_json(), assistent_companion.to_json()) )
            elif assistent_user is not None and assistent_user.access_token == access_token:
                return error("Чат может быть удален только студентом")
            else:
                return error("Чат не найден")


@app.post("/chat/send_message")
def send_message(id: int, text: str, access_token: str):
    text = text.strip()
    if text == "":
        return error("Пустое сообщение нельзя отправлять")
    if len(text) > MAX_MESSAGE_LENGTH:
        return error(f"Слишком длинное сообщение, оно более {MAX_MESSAGE_LENGTH} символов")

    with Session(engine) as session:
        statement = select(Chat).where(Chat.id == id)
        chat = session.exec(statement).first()

        if chat is None:
            return error("Чат не найден")
        else:
            statement = select(User).where(User.id == chat.student_id)
            student_user = session.exec(statement).first()
            if chat.companion_type == HUMAN:
                statement = select(User).where(User.id == chat.companion_id)
                assistent_user = session.exec(statement).first()
            else:
                assistent_user = None
            student_companion = ChatCompanion(HUMAN, student_user)
            assistent_companion = ChatCompanion(chat.companion_type, assistent_user)

            if student_user is not None and student_user.access_token == access_token:
                # Message sent by student
                message = Message(text=text,
                                  chat_id=chat.id,
                                  author_type=HUMAN,
                                  author_id=student_user.id)
                
                session.add(message)
                session.commit()
                
                # Если это LLM чат, создаем ответ от бота-заглушки с задержкой
                if chat.companion_type == LLM:
                    messages = session \
                        .exec(
                            select(Message) \
                                .where(Message.chat_id == chat.id)
                                .order_by(Message.id.desc())
                                .limit(HISTORY_SIZE)
                        ) \
                        .all()
                    
                    llm_history = []
                    for message in reversed(messages):
                        if message.author_type == STUDENT and message.author_id == student_user:
                            llm_history.append({ "author": "user", "text": message.text })
                        else:
                            llm_history.append({ "author": "assistant", "text": message.text })

                    response = requests.post(f"{LLM_API}/ask", params={
                        "chat_id": chat.id
                    }, json=llm_history)

                    print(f"Got responce with code {response.status_code}")

                return success( 
                    message.to_json(chat.to_json(student_user.to_json(),
                                                 assistent_companion.to_json()),
                                    student_companion.to_json())
                )
            elif assistent_user is not None and assistent_user.access_token == access_token:
                # Message sent by assistant
                message = Message(text=text,
                                  chat_id=chat.id,
                                  author_type=LLM,
                                  author_id=None)
                
                session.add(message)
                session.commit()

                return success(
                    message.to_json(chat.to_json(student_user.to_json(), 
                                                 assistent_companion.to_json()),
                                    (student_companion if student_user.id == message.author_id else assistent_companion).to_json())
                )
            elif chat.companion_type == LLM and access_token == LLM_CHAT_TOKEN:
                # Message sent by LLM
                message = Message(text=text,
                                  chat_id=chat.id,
                                  author_type=HUMAN,
                                  author_id=None)
                
                session.add(message)
                session.commit()

                return success(
                    message.to_json(chat.to_json(student_user.to_json(), 
                                                 assistent_companion.to_json()),
                                    (student_companion if student_user.id == message.author_id else assistent_companion).to_json())
                )
            else:
                return error("Чат не найден")


@app.get("/chat/history")
def read_history(id: int, access_token: str):
    with Session(engine) as session:
        statement = select(Chat).where(Chat.id == id)
        chat = session.exec(statement).first()

        if chat is None:
            return error("Чат не найден")
        else:
            statement = select(User).where(User.id == chat.student_id)
            student_user = session.exec(statement).first()
            if chat.companion_type == HUMAN:
                statement = select(User).where(User.id == chat.companion_id)
                assistent_user = session.exec(statement).first()
            else:
                assistent_user = None
            student_companion = ChatCompanion(HUMAN, student_user)
            assistent_companion = ChatCompanion(chat.companion_type, assistent_user)
            
            if student_user is not None and student_user.access_token == access_token or \
                    assistent_user is not None and assistent_user.access_token == access_token:
                statement = select(Message).where(Message.chat_id == chat.id)
                messages = session.exec(statement).all()

                return success(
                    list(map(
                        lambda message: message.to_json(
                            chat.to_json(student_user.to_json(), assistent_companion.to_json()), 
                            # Если author_id == 0, это сообщение от LLM
                            (ChatCompanion(LLM, None) if message.author_id == 0 
                             else (student_companion if student_user.id == message.author_id else assistent_companion)).to_json()
                        ),
                        messages
                    ))
                )
            else:
                return error("Чат не найден")


@app.get("/chats")
def read_chats(access_token: str):
    """Получить список всех чатов пользователя"""
    with Session(engine) as session:
        statement = select(User).where(User.access_token == access_token)
        user = session.exec(statement).first()

        if user is None:
            return error("Пользователь не найден")
        
        chats_list = []
        
        if user.status == STUDENT:
            # Студент видит только свои чаты
            statement = select(Chat).where(Chat.student_id == user.id)
            chats = session.exec(statement).all()
        elif user.status == ASSISTENT:
            # Ассистент видит чаты, где он является собеседником
            statement = select(Chat).where(Chat.companion_id == user.id)
            chats = session.exec(statement).all()
        else:
            return error("Неизвестный статус пользователя")
        
        for chat in chats:
            statement = select(User).where(User.id == chat.student_id)
            student_user = session.exec(statement).first()
            
            if chat.companion_type == HUMAN:
                statement = select(User).where(User.id == chat.companion_id)
                assistent_user = session.exec(statement).first()
            else:
                assistent_user = None
            assistent_companion = ChatCompanion(chat.companion_type, assistent_user)
            
            # Определяем title в зависимости от роли пользователя
            if user.status == STUDENT:
                title = chat.student_title
            else:
                title = chat.assistent_title
            
            chat_data = chat.to_json(student_user.to_json(), assistent_companion.to_json())
            chat_data['title'] = title
            chats_list.append(chat_data)
        
        return success(chats_list)

@app.post("/chat/switch_companion")
def switch_companion(id: int, access_token: str):
    with Session(engine) as session:
        statement = select(Chat).where(Chat.id == id)
        chat = session.exec(statement).first()

        if chat is None:
            return error("Чат не найден")
        else:
            statement = select(User).where(User.id == chat.student_id)
            student_user = session.exec(statement).first()
            if chat.companion_type == HUMAN:
                statement = select(User).where(User.id == chat.companion_id)
                assistent_user = session.exec(statement).first()
            else:
                assistent_user = None
            student_companion = ChatCompanion(HUMAN, student_user)
            assistent_companion = ChatCompanion(chat.companion_type, assistent_user)
            
            if student_user is not None and student_user.access_token == access_token:
                if chat.companion_type == HUMAN:
                    chat.companion_type = LLM
                    chat.companion_id = None

                    session.add(chat)
                    session.commit()
                    session.refresh(chat)

                    assistent_user = None
                    assistent_companion = ChatCompanion(chat.companion_type, assistent_user)

                    return success( chat.to_json(student_user.to_json(), assistent_companion.to_json()) )
                else:
                    response = requests.get(f"{AUTH_API}/assistent/available")

                    if response.status_code != 200:
                        return error("Внутренняя ошибка сервера")
                    
                    data = json.loads(response.text)

                    if not data['success']:
                        return error(f"Внутренняя ошибка сервера: " + data['error'])
                    
                    chat.companion_type = HUMAN
                    chat.companion_id = data['data']['id']

                    session.add(chat)
                    session.commit()
                    session.refresh(chat)

                    statement = select(User).where(User.id == data['data']['id'])
                    assistent_user = session.exec(statement).first()
                    assistent_companion = ChatCompanion(chat.companion_type, assistent_user)
                    
                    return success( chat.to_json(student_user.to_json(), assistent_companion.to_json()) )
            elif assistent_user is not None and assistent_user.access_token == access_token:
                return error("Менять собеседника может только студент")
            else:
                return error("Чат не найден")
#endregion