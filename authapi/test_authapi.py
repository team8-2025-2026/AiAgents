from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from main import app, get_session
from main import STUDENT, ASSISTENT
from main import ADMIN_ACCESS_TOKEN


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
        def get_session_override():
            return session 
        
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


def test_user_addition_failed_email():
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
