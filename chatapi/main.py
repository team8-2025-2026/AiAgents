from __future__ import annotations

from typing import Optional, Union
from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Field, Session, SQLModel, create_engine, select
from dataclasses import dataclass
import dotenv
from pathlib import Path
import bcrypt
import random
import string
import time
import os
import re
import threading
import requests


# Companion.type
HUMAN = "HUMAN"
LLM = "LLM"
STATUSES = [HUMAN, LLM]


# User.status
STUDENT = "STUDENT"
TEACHER = "TEACHER"
ASSISTENT = "ASSISTENT"
STATUSES = [STUDENT, TEACHER, ASSISTENT]


# LLM name and descrption
LLM_NAME = "Бот Ассистент"
LLM_DESCRIPION = "Я - учебный бот ассистент, " \
    "помогаю облегчить работу нашей тех поддержке, " \
    "отвечая на стандартные вопросы вместо них."


# Message constants
MAX_MESSAGE_LENGTH = 1024

# LLM API URL
LLM_API_URL = os.getenv('LLM_API_URL', 'http://localhost:8002')


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
    needs_teacher: bool         = Field(default=False)  # Флаг, что нейросеть запросила учителя

    def to_json(self, student_data: dict, assistent_companion_data: Optional[dict]) -> dict:
        return {
            "id": self.id,
            "student_title": self.student_title,
            "assistent_title": self.assistent_title,
            "student": student_data,
            "assistent": assistent_companion_data,
            "needs_teacher": self.needs_teacher
        }


class Message(SQLModel, table=True):
    id: Optional[int]           = Field(default=None, primary_key=True)
    text: str                   = Field()
    chat_id: int                = Field()
    author_id: int              = Field()

    def to_json(self, chat_data: dict, author_companion_data: dict) -> dict:
        return {
            "id": self.id,
            "text": self.text,
            "chat": chat_data,
            "author": author_companion_data,
        }


class TeacherRequest(SQLModel, table=True):
    """Заявка на подключение учителя к чату"""
    id: Optional[int]           = Field(default=None, primary_key=True)
    chat_id: int                = Field()  # ID чата, где нейросеть запросила учителя
    student_id: int             = Field()  # ID ученика
    question_message_id: int     = Field()  # ID сообщения, после которого нейросеть позвала учителя
    status: str                 = Field(default="PENDING")  # PENDING, ACCEPTED, REJECTED
    teacher_id: Optional[int]   = Field(default=None, nullable=True)  # ID учителя, который принял заявку
    created_at: float           = Field(default_factory=time.time)  # Время создания заявки

    def to_json(self, student_data: dict, teacher_data: Optional[dict] = None, question_text: str = "") -> dict:
        return {
            "id": self.id,
            "chat_id": self.chat_id,
            "student": student_data,
            "teacher": teacher_data,
            "question_message_id": self.question_message_id,
            "question_text": question_text,
            "status": self.status,
            "created_at": self.created_at
        }


# Загружаем .env файл из папки chatapi
env_path = Path(__file__).parent / ".env"
dotenv.load_dotenv(dotenv_path=env_path)
app = FastAPI()

connection_string = os.getenv('CONNECTION_STRING')
if connection_string is None:
    raise ValueError("CONNECTION_STRING не найден в .env файле. Создайте файл chatapi/.env с CONNECTION_STRING=sqlite:///database.db")

engine = create_engine(connection_string)
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
                message = Message(text=text,
                                  chat_id=chat.id,
                                  author_id=student_user.id)
                
                session.add(message)
                session.commit()
                
                # Если это LLM чат, создаем ответ от LLM API
                if chat.companion_type == LLM and not chat.needs_teacher:
                    # Запускаем создание ответа в отдельном потоке
                    def create_llm_response():
                        try:
                            # Получаем историю сообщений для контекста
                            with Session(engine) as history_session:
                                history_statement = select(Message).where(Message.chat_id == chat.id).order_by(Message.id)
                                history_messages = history_session.exec(history_statement).all()
                                
                                # Формируем историю для LLM API
                                llm_history = []
                                for msg in history_messages:
                                    if msg.author_id == student_user.id:
                                        llm_history.append({
                                            "text": msg.text,
                                            "author": "user"
                                        })
                                    elif msg.author_id == 0:
                                        llm_history.append({
                                            "text": msg.text,
                                            "author": "assistant"
                                        })
                                
                                # Добавляем системный промпт для определения необходимости учителя
                                system_prompt = """Ты - учебный бот ассистент. Твоя задача - отвечать на вопросы учеников.
Если вопрос требует экспертного мнения учителя или выходит за рамки твоих знаний, 
в конце ответа добавь специальный маркер: [NEEDS_TEACHER]
Обычные вопросы ты должен отвечать сам."""
                                
                                # Отправляем запрос в LLM API с системным промптом
                                llm_history_with_prompt = [
                                    {"text": system_prompt, "author": "system"}
                                ] + llm_history
                                
                                llm_response = requests.post(
                                    f"{LLM_API_URL}/ask",
                                    json=llm_history_with_prompt,
                                    timeout=60  # Таймаут 60 секунд
                                )
                                
                                if llm_response.status_code == 200:
                                    response_data = llm_response.json()
                                    if response_data.get("success") and "data" in response_data:
                                        llm_response_text = response_data["data"]["text"]
                                        
                                        # Проверяем, нужен ли учитель
                                        needs_teacher_marker = "[NEEDS_TEACHER]"
                                        needs_teacher = needs_teacher_marker in llm_response_text
                                        
                                        if needs_teacher:
                                            # Убираем маркер из ответа
                                            llm_response_text = llm_response_text.replace(needs_teacher_marker, "").strip()
                                            
                                            # Сохраняем ответ LLM (если он есть)
                                            with Session(engine) as response_session:
                                                if llm_response_text:
                                                    llm_message = Message(text=llm_response_text,
                                                                         chat_id=chat.id,
                                                                         author_id=0)
                                                    response_session.add(llm_message)
                                                
                                                # Устанавливаем флаг needs_teacher
                                                chat_statement = select(Chat).where(Chat.id == chat.id)
                                                current_chat = response_session.exec(chat_statement).first()
                                                if current_chat:
                                                    current_chat.needs_teacher = True
                                                
                                                # Создаем заявку на учителя
                                                teacher_request = TeacherRequest(
                                                    chat_id=chat.id,
                                                    student_id=student_user.id,
                                                    question_message_id=message.id,
                                                    status="PENDING"
                                                )
                                                response_session.add(teacher_request)
                                                
                                                # Отправляем сообщение ученику о подключении учителя
                                                teacher_notification = Message(
                                                    text="Ваш вопрос передан учителю. Ожидайте ответа.",
                                                    chat_id=chat.id,
                                                    author_id=0  # От системы
                                                )
                                                response_session.add(teacher_notification)
                                                
                                                response_session.commit()
                                        else:
                                            # Обычный ответ, сохраняем как обычно
                                            with Session(engine) as response_session:
                                                llm_message = Message(text=llm_response_text,
                                                                     chat_id=chat.id,
                                                                     author_id=0)  # 0 означает сообщение от LLM
                                                response_session.add(llm_message)
                                                response_session.commit()
                                    else:
                                        llm_response_text = "Извините, произошла ошибка при генерации ответа."
                                        with Session(engine) as response_session:
                                            llm_message = Message(text=llm_response_text,
                                                                 chat_id=chat.id,
                                                                 author_id=0)
                                            response_session.add(llm_message)
                                            response_session.commit()
                                else:
                                    llm_response_text = f"Ошибка LLM API: {llm_response.status_code}"
                                    with Session(engine) as response_session:
                                        llm_message = Message(text=llm_response_text,
                                                             chat_id=chat.id,
                                                             author_id=0)
                                        response_session.add(llm_message)
                                        response_session.commit()
                        except Exception as e:
                            print(f"Ошибка при запросе к LLM API: {str(e)}")
                            llm_response_text = "Извините, произошла ошибка при обращении к LLM API."
                            with Session(engine) as response_session:
                                llm_message = Message(text=llm_response_text,
                                                     chat_id=chat.id,
                                                     author_id=0)
                                response_session.add(llm_message)
                                response_session.commit()
                    
                    # Запускаем в отдельном потоке, чтобы не блокировать ответ
                    thread = threading.Thread(target=create_llm_response)
                    thread.daemon = True
                    thread.start()

                return success( 
                    message.to_json(chat.to_json(student_user.to_json(),
                                                 assistent_companion.to_json()),
                                    student_companion.to_json())
                )
            elif assistent_user is not None and assistent_user.access_token == access_token:
                message = Message(text=text,
                                  chat_id=chat.id,
                                  author_id=assistent_user.id)
                
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
        elif user.status == TEACHER or user.status == ASSISTENT:
            # Учитель/Ассистент видит чаты, где он является собеседником
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
#endregion

#region Teacher Requests
@app.get("/teacher_requests")
def get_teacher_requests(access_token: str):
    """Получить список заявок на подключение учителя"""
    with Session(engine) as session:
        statement = select(User).where(User.access_token == access_token)
        user = session.exec(statement).first()
        
        if user is None:
            return error("Пользователь не найден")
        
        if user.status != TEACHER and user.status != ASSISTENT:
            return error("Только учитель или ассистент могут просматривать заявки")
        
        # Получаем все заявки со статусом PENDING
        statement = select(TeacherRequest).where(TeacherRequest.status == "PENDING").order_by(TeacherRequest.created_at.desc())
        requests = session.exec(statement).all()
        
        requests_list = []
        for req in requests:
            # Получаем данные ученика
            student_statement = select(User).where(User.id == req.student_id)
            student = session.exec(student_statement).first()
            
            # Получаем текст вопроса
            question_statement = select(Message).where(Message.id == req.question_message_id)
            question_message = session.exec(question_statement).first()
            question_text = question_message.text if question_message else ""
            
            requests_list.append(req.to_json(
                student.to_json() if student else {},
                None,
                question_text
            ))
        
        return success(requests_list)


@app.post("/teacher_requests/{request_id}/accept")
def accept_teacher_request(request_id: int, access_token: str):
    """Принять заявку на подключение учителя и создать новый чат"""
    with Session(engine) as session:
        # Проверяем пользователя
        statement = select(User).where(User.access_token == access_token)
        teacher = session.exec(statement).first()
        
        if teacher is None:
            return error("Пользователь не найден")
        
        if teacher.status != TEACHER and teacher.status != ASSISTENT:
            return error("Только учитель или ассистент могут принимать заявки")
        
        # Получаем заявку
        statement = select(TeacherRequest).where(TeacherRequest.id == request_id)
        request = session.exec(statement).first()
        
        if request is None:
            return error("Заявка не найдена")
        
        if request.status != "PENDING":
            return error("Заявка уже обработана")
        
        # Получаем исходный чат
        statement = select(Chat).where(Chat.id == request.chat_id)
        original_chat = session.exec(statement).first()
        
        if original_chat is None:
            return error("Исходный чат не найден")
        
        # Получаем данные ученика
        statement = select(User).where(User.id == request.student_id)
        student = session.exec(statement).first()
        
        if student is None:
            return error("Ученик не найден")
        
        # Создаем новый чат с учителем
        new_chat = Chat(
            student_title=f"Чат с учителем (из чата #{original_chat.id})",
            assistent_title=f"Чат с {student.first_name} {student.last_name}",
            companion_type=HUMAN,
            companion_id=teacher.id,
            student_id=student.id,
            needs_teacher=False
        )
        session.add(new_chat)
        session.commit()
        session.refresh(new_chat)
        
        # Копируем историю сообщений до момента вызова учителя
        statement = select(Message).where(
            Message.chat_id == original_chat.id,
            Message.id <= request.question_message_id
        ).order_by(Message.id)
        original_messages = session.exec(statement).all()
        
        for orig_msg in original_messages:
            # Определяем автора сообщения
            if orig_msg.author_id == student.id:
                new_author_id = student.id
            elif orig_msg.author_id == 0:
                new_author_id = 0  # LLM сообщения
            else:
                new_author_id = orig_msg.author_id
            
            new_message = Message(
                text=orig_msg.text,
                chat_id=new_chat.id,
                author_id=new_author_id
            )
            session.add(new_message)
        
        # Добавляем системное сообщение о том, что учитель подключился
        system_message = Message(
            text=f"Учитель {teacher.first_name} {teacher.last_name} подключился к чату.",
            chat_id=new_chat.id,
            author_id=0  # От системы
        )
        session.add(system_message)
        
        # Обновляем статус заявки
        request.status = "ACCEPTED"
        request.teacher_id = teacher.id
        session.add(request)
        
        session.commit()
        
        # Формируем ответ
        student_companion = ChatCompanion(HUMAN, student)
        teacher_companion = ChatCompanion(HUMAN, teacher)
        
        return success(new_chat.to_json(student.to_json(), teacher_companion.to_json()))
#endregion