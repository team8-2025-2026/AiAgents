from __future__ import annotations

from typing import Optional, Union
from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from sqlmodel import Field, Session, SQLModel, create_engine, select
from dotenv import load_dotenv
import bcrypt
import random
import string
import time
import os
import re


# User.status
STUDENT = "STUDENT"
TEACHER = "TEACHER"
ASSISTENT = "ASSISTENT"
STATUSES = [STUDENT, TEACHER, ASSISTENT]


# Password utils constants
AVAILABLE_PASSWORD_SYMBOLS = string.ascii_letters + string.digits
PASSWORD_LENGTH = 20


# Validation constants
EMAIL_REGEX = re.compile(r"[^@]+@[^@]+\.[^@]+")
EMAIL_LENGTH_RANGE = range(1, 256)
FIRST_NAME_LENGTH_RANGE = range(2, 64)
LAST_NAME_LENGTH_RANGE = range(2, 64)
PASSWORD_LENGTH_RANGE = range(8, 32)
DESCRIPTION_LENGTH_RANGE = range(0, 1024)


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    first_name: str = Field()
    last_name: str = Field()
    status: str = Field()
    description: str = Field(default="")
    password_hash: str = Field()
    access_token: str = Field(unique=True, index=True)

    def to_json(self) -> dict:
        return {
            "id": self.id,
            "email": self.email,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "status": self.status,
            "description": self.description,
            "access_token": self.access_token
        }


engine = create_engine("sqlite:///database.db")
app = FastAPI()
salt = bcrypt.gensalt()

load_dotenv()
SQLModel.metadata.create_all(engine)

# CORS middleware для работы с фронтендом
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В продакшене указать конкретные домены
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


#region Password utils
def check_password_hash(password: str,
                        password_hash: str):
    return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))


def generate_password():
    passwd = random.choices(AVAILABLE_PASSWORD_SYMBOLS, k=PASSWORD_LENGTH)
    return "".join(passwd)


def generate_password_hash(password: str):
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode()


def generate_access_token(email: str, password: str):
    return bcrypt.hashpw((email + str(time.time()) + password).encode('utf-8'), salt).decode()
#endregion


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


#region Validation utils
def validate_email(email: str) -> bool:
    return len(email) in EMAIL_LENGTH_RANGE and EMAIL_REGEX.match(email)


def validate_first_name(first_name: str) -> bool:
    return len(first_name) in FIRST_NAME_LENGTH_RANGE


def validate_last_name(last_name: str) -> bool:
    return len(last_name) in LAST_NAME_LENGTH_RANGE


def validate_description(description: str) -> bool:
    return len(description) in DESCRIPTION_LENGTH_RANGE


def validate_password(password: str) -> bool:
    return len(password) in PASSWORD_LENGTH_RANGE


def validate_status(status: str) -> bool:
    return status in STATUSES
#endregion


#region CRUD
@app.get("/user")
def read_user(email: str,
              password: str):
    with Session(engine) as session:
        statement = select(User).where(User.email == email)
        user = session.exec(statement).first()

        if user is not None and check_password_hash(password, user.password_hash):
            return success(user.to_json())
        else:
            return error("Пользователь с таким email и паролем не найден")


@app.get("/user/by_token")
def read_user_by_token(access_token: str):
    with Session(engine) as session:
        statement = select(User).where(User.access_token == access_token)
        user = session.exec(statement).first()

        if user is not None:
            return success(user.to_json())
        else:
            return error("Пользователь с таким токеном не найден")


@app.put("/user")
def create_user(email: str,
                first_name: str,
                last_name: str,
                status: str,
                access_token: str):
    with Session(engine) as session:
        statement = select(User).where(User.email == email)
        user = session.exec(statement).first()

        if user is not None:
            return error("Email занят")
    
    if not validate_email(email):
        return error("Неверные параметры: email")
    if not validate_first_name(first_name):
        return error("Неверные параметры: first_name")
    if not validate_last_name(last_name):
        return error("Неверные параметры: last_name")
    if not validate_status(status):
        return error("Неверные параметры: status")
    
    # Check access permissions
    if access_token != os.getenv('ADMIN_ACCESS_TOKEN'):
        with Session(engine) as session:
            statement = select(User).where(User.access_token == access_token)
            user = session.exec(statement).first()

            if user is None or user.status != ASSISTENT:
                return error("Недостаточно прав")

    with Session(engine) as session:
        password = generate_password()
        password_hash = generate_password_hash(password)
        access_token = generate_access_token(email, password)
        new_user = User(email=email,
                        first_name=first_name,
                        last_name=last_name,
                        status=status,
                        password_hash=password_hash,
                        access_token=access_token)
        session.add(new_user)
        session.commit()

        output_data = new_user.to_json()
        output_data['password'] = password

        return success(output_data)


@app.patch("/user")
def update_user(email: str,
                access_token: str,
                first_name: Optional[str] = None,
                last_name: Optional[str] = None,
                description: Optional[str] = None,
                password: Optional[str] = None):
    if first_name is not None and not validate_first_name(first_name):
        return error("Неверные параметры: first_name")
    if last_name is not None and not validate_last_name(last_name):
        return error("Неверные параметры: last_name")
    if description is not None and not validate_description(description):
        return error("Неверные параметры: description")
    if password is not None and not validate_password(password):
        return error("Неверные параметры: password")
    
    # Check access permissions
    if access_token != os.getenv('ADMIN_ACCESS_TOKEN'):
        with Session(engine) as session:
            statement = select(User).where(User.access_token == access_token)
            user = session.exec(statement).first()

            if user is None:
                return error("Недостаточно прав")
            elif user.email == email: # User changes its own settings
                pass
            elif user.status == ASSISTENT: # Assistent changes user settings
                statement = select(User).where(User.email == email)
                user = session.exec(statement).first()
                
                if user is None:
                    return error("Почта не найдена")
                elif user.status == ASSISTENT:
                    return error("Недостаточно прав(ассистент не может обновлять данные другого ассистента)")
                else:
                    pass
            else:
                return error("Недостаточно прав")
    
    # Update data
    with Session(engine) as session:
        statement = select(User).where(User.email == email)
        user = session.exec(statement).first()
        
        if first_name is not None:
            user.first_name = first_name
        if last_name is not None:
            user.last_name = last_name
        if description is not None:
            user.description = description
        if password is not None:
            user.password_hash = generate_password_hash(password)
        
        session.add(user)
        session.commit()
        session.refresh(user)

        return success(user.to_json())


@app.delete("/user")
def delete_user(email: str,
                access_token: str):
    # Check access permissions
    if access_token != os.getenv('ADMIN_ACCESS_TOKEN'):
        with Session(engine) as session:
            statement = select(User).where(User.access_token == access_token)
            user = session.exec(statement).first()

            if user is None:
                return error("Недостаточно прав")
            elif user.email == email: # User deletes its own account
                pass
            elif user.status == ASSISTENT: # Assistent deletes user settings
                statement = select(User).where(User.email == email)
                user = session.exec(statement).first()
                
                if user is None:
                    return error("Почта не найдена")
                elif user.status == ASSISTENT:
                    return error("Недостаточно прав(ассистент не может удалять аккаунт другого ассистента)")
                else:
                    pass
            else:
                return error("Недостаточно прав")
    
    # Delete data
    with Session(engine) as session:
        statement = select(User).where(User.email == email)
        user = session.exec(statement).first()
        
        session.delete(user)
        session.commit()

        return success(user.to_json())
#endregion


#region Web UI
@app.get("/", response_class=HTMLResponse)
async def root():
    """Главная страница с формой авторизации"""
    html_content = """
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>AI Agents - Вход в систему</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu', 'Cantarell', sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                display: flex;
                justify-content: center;
                align-items: center;
                min-height: 100vh;
                padding: 20px;
            }
            .container {
                background: #202123;
                padding: 2rem 3rem;
                border-radius: 12px;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
                width: 100%;
                max-width: 400px;
            }
            h1 {
                text-align: center;
                margin-bottom: 0.5rem;
                font-size: 2rem;
                color: #ececf1;
            }
            h2 {
                text-align: center;
                margin-bottom: 2rem;
                font-size: 1.2rem;
                color: #8e8ea0;
                font-weight: normal;
            }
            .form-group {
                display: flex;
                flex-direction: column;
                gap: 0.5rem;
                margin-bottom: 1.5rem;
            }
            label {
                font-size: 0.9rem;
                color: #8e8ea0;
            }
            input {
                padding: 0.75rem;
                background: #40414f;
                border: 1px solid #565869;
                border-radius: 6px;
                color: #ececf1;
                font-size: 1rem;
                transition: border-color 0.2s;
            }
            input:focus {
                outline: none;
                border-color: #10a37f;
            }
            button {
                width: 100%;
                padding: 0.75rem;
                background: #10a37f;
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 1rem;
                font-weight: 500;
                cursor: pointer;
                transition: background 0.2s;
            }
            button:hover {
                background: #0d8f6e;
            }
            button:disabled {
                opacity: 0.6;
                cursor: not-allowed;
            }
            .error {
                background: #ef4444;
                color: white;
                padding: 0.75rem;
                border-radius: 6px;
                font-size: 0.9rem;
                text-align: center;
                margin-bottom: 1rem;
                display: none;
            }
            .success {
                background: #10a37f;
                color: white;
                padding: 0.75rem;
                border-radius: 6px;
                font-size: 0.9rem;
                text-align: center;
                margin-bottom: 1rem;
                display: none;
            }
            .note {
                margin-top: 1.5rem;
                text-align: center;
                font-size: 0.85rem;
                color: #8e8ea0;
            }
            .api-link {
                margin-top: 1rem;
                text-align: center;
            }
            .api-link a {
                color: #10a37f;
                text-decoration: none;
                font-size: 0.9rem;
            }
            .api-link a:hover {
                text-decoration: underline;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>AI Agents</h1>
            <h2>Вход в систему</h2>
            <div id="error" class="error"></div>
            <div id="success" class="success"></div>
            <form id="loginForm">
                <div class="form-group">
                    <label for="email">Email</label>
                    <input type="email" id="email" name="email" required placeholder="example@mail.com">
                </div>
                <div class="form-group">
                    <label for="password">Пароль</label>
                    <input type="password" id="password" name="password" required placeholder="Введите пароль">
                </div>
                <button type="submit" id="submitBtn">Войти</button>
            </form>
            <p class="note">Создание аккаунта доступно только через поддержку</p>
            <div class="api-link">
                <a href="/docs" target="_blank">API Документация</a> | 
                <a href="https://github.com" target="_blank" style="margin-left: 0.5rem;">Инструкция по регистрации</a>
            </div>
        </div>
        <script>
            const form = document.getElementById('loginForm');
            const errorDiv = document.getElementById('error');
            const successDiv = document.getElementById('success');
            const submitBtn = document.getElementById('submitBtn');

            form.addEventListener('submit', async (e) => {
                e.preventDefault();
                errorDiv.style.display = 'none';
                successDiv.style.display = 'none';
                submitBtn.disabled = true;
                submitBtn.textContent = 'Вход...';

                const email = document.getElementById('email').value;
                const password = document.getElementById('password').value;

                try {
                    const params = new URLSearchParams({ email, password });
                    const response = await fetch(`/user?${params.toString()}`);
                    const data = await response.json();

                    if (data.success) {
                        // Сохраняем токен и данные пользователя
                        localStorage.setItem('access_token', data.data.access_token);
                        localStorage.setItem('user_data', JSON.stringify(data.data));
                        
                        successDiv.textContent = 'Успешный вход! Перенаправление...';
                        successDiv.style.display = 'block';
                        
                        // Перенаправляем на главную страницу WebUI (если запущен)
                        setTimeout(() => {
                            window.location.href = 'http://localhost:3000';
                        }, 1000);
                    } else {
                        errorDiv.textContent = data.error || 'Ошибка авторизации';
                        errorDiv.style.display = 'block';
                        submitBtn.disabled = false;
                        submitBtn.textContent = 'Войти';
                    }
                } catch (error) {
                    errorDiv.textContent = 'Ошибка подключения к серверу';
                    errorDiv.style.display = 'block';
                    submitBtn.disabled = false;
                    submitBtn.textContent = 'Войти';
                }
            });
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)
#endregion
