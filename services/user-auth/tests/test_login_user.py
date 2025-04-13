import pytest
import os
import logging
import jwt
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError
from sqlalchemy.sql import text
from sqlalchemy import select
from app.main import app, Base
from app.core.config import settings
from app.routers.user_router import get_db
from datetime import datetime, timedelta

# Configurar logging para suprimir mensajes de FastAPI
logging.getLogger("uvicorn").setLevel(logging.WARNING)
logging.getLogger("fastapi").setLevel(logging.WARNING)

# Usar la URL de la base de datos de la variable de entorno si está disponible, o db como fallback
TEST_DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://user:password@db:5432/student_management"
)
engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def create_test_database():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except OperationalError:
        # Usar la misma URL base pero con la base de datos postgres
        root_url = TEST_DATABASE_URL.replace("/student_management", "/postgres")
        root_engine = create_engine(root_url)
        with root_engine.connect() as connection:
            connection.execution_options(isolation_level="AUTOCOMMIT").execute(
                text("CREATE DATABASE student_management")
            )


create_test_database()

Base.metadata.create_all(bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture
def client():
    return TestClient(app, base_url="http://testserver")


@pytest.fixture(scope="function")
def setup_test_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def expect_error_response(response, status_code: int):
    assert response.status_code == status_code
    data = response.json()
    assert "type" in data
    assert "title" in data
    assert "status" in data
    assert "detail" in data
    assert "instance" in data


def register_user(
    client, name="John Doe", email="john@example.com", password="password123"
):
    return client.post(
        "/api/v1/register",
        json={"name": name, "email": email, "password": password},
    )


def login_user(client, email="john@example.com", password="password123"):
    return client.post(
        "/api/v1/token",
        data={"username": email, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )


def test_login_success_with_valid_email_and_password(client, setup_test_db):
    # Login exitoso con credenciales validas
    # Primero, registra un usuario
    register_user(client)
    # Luego, intenta iniciar sesión
    response = login_user(client)

    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_fail_with_wrong_password(client, setup_test_db):
    # Contrasena incorrecta

    register_user(client)

    response = login_user(client, password="wrongpassword")

    expect_error_response(response, 401)


def test_login_fail_with_invalid_email_format(client, setup_test_db):
    # Formato de email invalido

    response = login_user(client, email="invalidemail")

    expect_error_response(response, 400)


def test_login_fail_with_empty_password(client, setup_test_db):
    # Contraseña vacia
    register_user(client)

    response = login_user(client, password="")

    expect_error_response(response, 400)


def test_login_fail_with_empty_email(client, setup_test_db):
    # Email vacío

    response = login_user(client, email="")

    expect_error_response(response, 400)


def test_login_fail_with_nonexistent_user(client, setup_test_db):
    # Usuario no registrado
    response = login_user(client, email="nonexistentuser@example.com")

    expect_error_response(response, 401)


def test_protected_route_with_valid_token(client, setup_test_db):
    # Ruta protegida con token valido
    register_user(client)
    response = login_user(client)
    data = response.json()
    token = data["access_token"]

    response = client.get(
        "/api/v1/users/me/",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert "email" in data
    assert "name" in data


def generate_expired_token(email):
    # Simula un token expirado
    to_encode = {"sub": email}
    expire = datetime.now() - timedelta(minutes=1)  # Tiempo = expirado
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def test_session_expired(client, setup_test_db):
    register_user(client)
    token = generate_expired_token(email="john@example.com")

    response = client.get(
        "/api/v1/users/me/",
        headers={"Authorization": f"Bearer {token}"},
    )
    expect_error_response(response, 401)


def test_login_fail_with_blocked_user(client, setup_test_db):
    # Intento de login con usuario bloqueado
    register_user(client)

    from app.models.user import User

    db = TestingSessionLocal()
    user = db.query(User).filter(User.email == "john@example.com").first()
    db.close()

    # Bloquear el usuario
    user.is_blocked = True

    db = TestingSessionLocal()
    db.add(user)
    db.commit()
    db.close()

    # Luego, intenta iniciar sesión
    response = login_user(client)

    expect_error_response(response, 403)


def test_account_locks_after_failed_attempts(client, setup_test_db):
    # Se bloquea la cuenta luego de varios intentos fallidos
    register_user(client)
    # Intenta iniciar sesión con credenciales incorrectas varias veces
    for _ in range(4):
        response = login_user(client, password="wrongpassword")
        expect_error_response(response, 401)
    # Luego, intenta iniciar sesión nuevamente, debería bloquearse
    response = login_user(client, password="wrongpassword")
    expect_error_response(response, 403)
