from typing import Optional, Union
from fastapi import Depends, FastAPI, HTTPException, Query
from sqlmodel import Field, Session, SQLModel, create_engine, select
from dotenv import load_dotenv
import bcrypt
import random
import string
import time
import os


# User.status
STUDENT = "STUDENT"
TEACHER = "TEACHER"
ASSISTENT = "ASSISTENT"
STATUSES = [STUDENT, TEACHER, ASSISTENT]


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


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/user")
def read_user(email: str,
              password: str):
    with Session(engine) as session:
        statement = select(User).where(User.email == email)
        user = session.exec(statement).first()

        if user is not None and bcrypt.checkpw(password.encode('utf-8'), user.password_hash.encode('utf-8')):
            return {
                "success": True,
                "data": user.to_json()
            }
        else:
            return {
                "success": False,
                "error": "Пользователь с таким email и паролем не найден"
            }
        

AVAILABLE_PASSWORD_SYMBOLS = string.ascii_letters + string.digits
PASSWORD_LENGTH = 20
def generate_password():
    passwd = random.choices(AVAILABLE_PASSWORD_SYMBOLS, k=PASSWORD_LENGTH)
    return "".join(passwd)


def generate_password_hash(password: str):
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode()


def generate_access_token(email: str, password: str):
    return bcrypt.hashpw((email + str(time.time()) + password).encode('utf-8'), salt).decode()


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
            return {
                "success": False,
                "error": "Email занят"
            }
    
    if len(first_name) not in range(2, 30):
        return {
            "success": False,
            "error": "Невалидное имя пользователя"
        }
    if len(last_name) not in range(2, 30):
        return {
            "success": False,
            "error": "Невалидная фамилия пользователя"
        }
    if status not in STATUSES:
        return {
            "success": False,
            "error": "Невалидный статус пользователя"
        }
    
    # Check access permissions
    if access_token != os.getenv('ADMIN_ACCESS_TOKEN'):
        with Session(engine) as session:
            statement = select(User).where(User.access_token == access_token)
            user = session.exec(statement).first()

            if user is None or user.status != ASSISTENT:
                return {
                    "success": False,
                    "error": "Недостаточно прав"
                }

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

        return {
            "success": True,
            "data": output_data
        }
