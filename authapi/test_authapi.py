from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from .main import app, get_session
from .main import STUDENT, ASSISTENT
from .main import ADMIN_ACCESS_TOKEN


client = TestClient(app)


def test_get_not_existing_user():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool, 
    )
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:  
        def get_session_override():
            return session 
        
        app.dependency_overrides[get_session] = get_session_override 
        response = client.get("/user", params={
            "email": "testemail@google.com",
            "password": "testpassword"
        })

        app.dependency_overrides.clear()
        assert response.status_code == 200
        assert response.json() == {
            "success": False,
            "error": "Пользователь с таким email и паролем не найден"
        }


def test_user_addition_success():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool, 
    )
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        get_session_override = lambda: session
        app.dependency_overrides[get_session] = get_session_override

        response = client.put("/user", params={
            "email": "testemail@google.com",
            "first_name": "testfirstname",
            "last_name": "testlastname",
            "status": STUDENT,
            "access_token": ADMIN_ACCESS_TOKEN,
        })
        app.dependency_overrides.clear()

        assert response.status_code == 200
        assert response.json()['success'] == True
        assert response.json().get('data') is not None
        assert response.json()['data'].get('email') == "testemail@google.com"
        assert response.json()['data'].get('first_name') == "testfirstname"
        assert response.json()['data'].get('last_name') == "testlastname"
        assert response.json()['data'].get('status') == STUDENT
        assert response.json()['data'].get('access_token') is not None
        assert response.json()['data'].get('password') is not None

        app.dependency_overrides[get_session] = get_session_override 
        response = client.get("/user", params={
            "email": "testemail@google.com",
            "password": response.json()['data']['password']
        })
        app.dependency_overrides.clear()

        assert response.json()['success'] == True
        assert response.json().get('data') is not None
        assert response.json()['data'].get('email') == "testemail@google.com"
        assert response.json()['data'].get('first_name') == "testfirstname"
        assert response.json()['data'].get('last_name') == "testlastname"
        assert response.json()['data'].get('status') == STUDENT
        assert response.json()['data'].get('access_token') is not None
        assert response.json()['data'].get('password') is None


def test_user_addition_failed():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool, 
    )
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        get_session_override = lambda: session
        app.dependency_overrides[get_session] = get_session_override
        
        valid_params = {
            "email": "testemail@google.com",
            "first_name": "testfirstname",
            "last_name": "testlastname",
            "status": STUDENT,
            "access_token": ADMIN_ACCESS_TOKEN,
        }

        # Test if email is invalid
        invalid_params_email = valid_params.copy()
        invalid_params_email['email'] = "qwerty"
        response = client.put("/user", params=invalid_params_email)

        assert response.status_code == 200
        assert response.json()['success'] == False
        assert response.json()['error'] == "Неверные параметры: email"

        # Test if first name is invalid
        invalid_params_first_name = valid_params.copy()
        invalid_params_first_name['first_name'] = "q"
        response = client.put("/user", params=invalid_params_first_name)

        assert response.status_code == 200
        assert response.json()['success'] == False
        assert response.json()['error'] == "Неверные параметры: first_name"

        # Test if last name is invalid
        invalid_params_last_name = valid_params.copy()
        invalid_params_last_name['last_name'] = "q"
        response = client.put("/user", params=invalid_params_last_name)

        assert response.status_code == 200
        assert response.json()['success'] == False
        assert response.json()['error'] == "Неверные параметры: last_name"

        # Test if status is invalid
        invalid_params_status = valid_params.copy()
        invalid_params_status['status'] = "qqq"
        response = client.put("/user", params=invalid_params_status)

        assert response.status_code == 200
        assert response.json()['success'] == False
        assert response.json()['error'] == "Неверные параметры: status"

        app.dependency_overrides.clear()


def test_user_self_edit():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool, 
    )
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        get_session_override = lambda: session
        app.dependency_overrides[get_session] = get_session_override

        # Создание тестового аккаунта
        response = client.put("/user", params={
            "email": "testemail@google.com",
            "first_name": "testfirstname",
            "last_name": "testlastname",
            "status": STUDENT,
            "access_token": ADMIN_ACCESS_TOKEN,
        })

        assert response.status_code == 200
        assert response.json()['success'] == True
        user_data = response.json()['data']
        
        # Смена пароля аккаунта
        response = client.patch("/user", params={
            "email": user_data['email'],
            "password": "newpassword",
            "access_token": user_data['access_token'],
        })

        assert response.status_code == 200
        assert response.json()['success'] == True
        
        # Проверка, что пароль сменился
        response = client.get("/user", params={
            "email": user_data['email'],
            "password": "newpassword",
        })

        assert response.status_code == 200
        assert response.json()['success'] == True

        app.dependency_overrides.clear()


def test_user_tries_to_edit_other():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool, 
    )
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        get_session_override = lambda: session
        app.dependency_overrides[get_session] = get_session_override
        
        # Создание тестового аккаунта
        response = client.put("/user", params={
            "email": "testemail@google.com",
            "first_name": "testfirstname",
            "last_name": "testlastname",
            "status": STUDENT,
            "access_token": ADMIN_ACCESS_TOKEN,
        })

        assert response.status_code == 200
        assert response.json()['success'] == True
        user_data1 = response.json()['data']

        # Создание тестового аккаунта #2
        response = client.put("/user", params={
            "email": "testemail2@google.com",
            "first_name": "testfirstname2",
            "last_name": "testlastname2",
            "status": STUDENT,
            "access_token": ADMIN_ACCESS_TOKEN,
        })

        assert response.status_code == 200
        assert response.json()['success'] == True
        user_data2 = response.json()['data']
        
        # Смена пароля аккаунта
        response = client.patch("/user", params={
            "email": "testemail2@google.com",
            "password": "newpassword",
            "access_token": user_data1['access_token'],
        })

        assert response.status_code == 200
        assert response.json()['success'] == False
        assert response.json()['error'] == "Недостаточно прав"
        app.dependency_overrides.clear()


def test_assistent_edits_student():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool, 
    )
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        get_session_override = lambda: session
        app.dependency_overrides[get_session] = get_session_override

        # Создание тестового аккаунта
        response = client.put("/user", params={
            "email": "testemail1@google.com",
            "first_name": "testfirstname",
            "last_name": "testlastname",
            "status": STUDENT,
            "access_token": ADMIN_ACCESS_TOKEN,
        })

        assert response.status_code == 200
        assert response.json()['success'] == True
        user_data1 = response.json()['data']

        # Создание тестового аккаунта #2
        response = client.put("/user", params={
            "email": "testemail2@google.com",
            "first_name": "testfirstname2",
            "last_name": "testlastname2",
            "status": ASSISTENT,
            "access_token": ADMIN_ACCESS_TOKEN,
        })

        assert response.status_code == 200
        assert response.json()['success'] == True
        user_data2 = response.json()['data']
        
        # Смена пароля аккаунта
        response = client.patch("/user", params={
            "email": user_data1['email'],
            "password": "newpassword",
            "access_token": user_data2['access_token'],
        })

        assert response.status_code == 200
        assert response.json()['success'] == True
        
        # Проверка, что пароль сменился
        response = client.get("/user", params={
            "email": user_data1['email'],
            "password": "newpassword",
        })

        assert response.status_code == 200
        assert response.json()['success'] == True

        app.dependency_overrides.clear()


def test_user_self_delete():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool, 
    )
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        get_session_override = lambda: session
        app.dependency_overrides[get_session] = get_session_override

        # Создание тестового аккаунта
        response = client.put("/user", params={
            "email": "testemail1@google.com",
            "first_name": "testfirstname",
            "last_name": "testlastname",
            "status": STUDENT,
            "access_token": ADMIN_ACCESS_TOKEN,
        })

        assert response.status_code == 200
        assert response.json()['success'] == True
        user_data1 = response.json()['data']
        
        # Проверка, что юзер существует
        response = client.get("/user", params={
            "email": user_data1['email'],
            "password": user_data1['password'],
        })

        assert response.status_code == 200
        assert response.json()['success'] == True

        # Удаление тестового аккаунта
        response = client.delete("/user", params={
            "email": user_data1['email'],
            "access_token": user_data1['access_token'],
        })

        assert response.status_code == 200
        assert response.json()['success'] == True
        
        # Проверка, что юзер перестал существовать
        response = client.get("/user", params={
            "email": user_data1['email'],
            "password": user_data1['password'],
        })

        assert response.status_code == 200
        assert response.json()['success'] == False

        app.dependency_overrides.clear()


def test_user_delete_by_assistent():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool, 
    )
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        get_session_override = lambda: session
        app.dependency_overrides[get_session] = get_session_override
        
        # Создание тестового аккаунта
        response = client.put("/user", params={
            "email": "testemail1@google.com",
            "first_name": "testfirstname",
            "last_name": "testlastname",
            "status": STUDENT,
            "access_token": ADMIN_ACCESS_TOKEN,
        })

        assert response.status_code == 200
        assert response.json()['success'] == True
        user_data1 = response.json()['data']
        
        # Создание тестового ассистента
        response = client.put("/user", params={
            "email": "testemail2@google.com",
            "first_name": "testfirstname",
            "last_name": "testlastname",
            "status": ASSISTENT,
            "access_token": ADMIN_ACCESS_TOKEN,
        })

        assert response.status_code == 200
        assert response.json()['success'] == True
        user_data2 = response.json()['data']
        
        # Проверка, что юзер существует
        response = client.get("/user", params={
            "email": user_data1['email'],
            "password": user_data1['password'],
        })

        assert response.status_code == 200
        assert response.json()['success'] == True

        # Удаление тестового аккаунта
        response = client.delete("/user", params={
            "email": user_data1['email'],
            "access_token": user_data2['access_token'],
        })

        assert response.status_code == 200
        assert response.json()['success'] == True
        
        # Проверка, что юзер перестал существовать
        response = client.get("/user", params={
            "email": user_data1['email'],
            "password": user_data1['password'],
        })

        assert response.status_code == 200
        assert response.json()['success'] == False

        app.dependency_overrides.clear()


def test_user_tries_to_delete_other():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool, 
    )
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        get_session_override = lambda: session
        app.dependency_overrides[get_session] = get_session_override
        
        # Создание тестового аккаунта
        response = client.put("/user", params={
            "email": "testemail1@google.com",
            "first_name": "testfirstname",
            "last_name": "testlastname",
            "status": STUDENT,
            "access_token": ADMIN_ACCESS_TOKEN,
        })

        assert response.status_code == 200
        assert response.json()['success'] == True
        user_data1 = response.json()['data']
        
        # Создание тестового ассистента
        response = client.put("/user", params={
            "email": "testemail2@google.com",
            "first_name": "testfirstname",
            "last_name": "testlastname",
            "status": STUDENT,
            "access_token": ADMIN_ACCESS_TOKEN,
        })

        assert response.status_code == 200
        assert response.json()['success'] == True
        user_data2 = response.json()['data']
        
        # Проверка, что юзер существует
        response = client.get("/user", params={
            "email": user_data1['email'],
            "password": user_data1['password'],
        })

        assert response.status_code == 200
        assert response.json()['success'] == True

        # Неудачное удаление чужого аккаунта
        response = client.delete("/user", params={
            "email": user_data1['email'],
            "access_token": user_data2['access_token'],
        })

        assert response.status_code == 200
        assert response.json()['success'] == False
        assert response.json()['error'] == "Недостаточно прав"
        
        # Проверка, что юзер сущесвтует
        response = client.get("/user", params={
            "email": user_data1['email'],
            "password": user_data1['password'],
        })

        assert response.status_code == 200
        assert response.json()['success'] == True

        app.dependency_overrides.clear()
