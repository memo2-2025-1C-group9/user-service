import pytest
import os
import logging
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError
from sqlalchemy.sql import text
from app.main import app, Base
from app.routers.user_router import get_db
from unittest.mock import MagicMock, patch

# Configurar logging para suprimir mensajes de FastAPI
logging.getLogger("uvicorn").setLevel(logging.WARNING)
logging.getLogger("fastapi").setLevel(logging.WARNING)

# Usar la URL de la base de datos desde las variables de entorno
TEST_DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}?sslmode=require",
)
engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def create_test_database():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except OperationalError:
        # Usar la misma URL base pero con la base de datos postgres
        root_url = TEST_DATABASE_URL.replace(f"/{os.getenv('DB_NAME')}", "/postgres")
        root_engine = create_engine(root_url)
        with root_engine.connect() as connection:
            connection.execution_options(isolation_level="AUTOCOMMIT").execute(
                text(f"CREATE DATABASE {os.getenv('DB_NAME')}")
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
    # Limpiar las tablas antes de cada test
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    # Limpiar las tablas después de cada test
    Base.metadata.drop_all(bind=engine)


def test_register_user(client, setup_test_db):
    # Registrar un usuario correctamente
    response = client.post(
        "/api/v1/register",
        json={
            "name": "John Doe",
            "email": "john@example.com",
            "password": "password123",
            "location": "Buenos Aires",
        },
    )
    assert response.status_code == 200
    assert response.json()["status"] == "success"
    assert "location" in response.json()["data"]
    assert response.json()["data"]["location"] == "Buenos Aires"


def test_register_duplicate_user(client, setup_test_db):
    # Registrar primer usuario
    client.post(
        "/api/v1/register",
        json={
            "name": "John Doe",
            "email": "john@example.com",
            "password": "password123",
            "location": "Buenos Aires",
        },
    )

    # Intentar registrar el mismo usuario nuevamente
    response = client.post(
        "/api/v1/register",
        json={
            "name": "John Doe",
            "email": "john@example.com",
            "password": "password123",
            "location": "Buenos Aires",
        },
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "El email ya está registrado"


def test_register_user_without_location(client, setup_test_db):
    # Registrar un usuario sin location (debería ser opcional)
    response = client.post(
        "/api/v1/register",
        json={
            "name": "John Doe",
            "email": "john@example.com",
            "password": "password123",
        },
    )
    assert response.status_code == 200
    assert response.json()["status"] == "success"
    assert response.json()["data"]["location"] is None


def test_register_user_invalid_email(client, setup_test_db):
    # Intentar registrar un usuario con email inválido
    response = client.post(
        "/api/v1/register",
        json={
            "name": "John Doe",
            "email": "invalid-email",
            "password": "password123",
            "location": "Buenos Aires",
        },
    )
    assert response.status_code == 422
    # Verificar que el mensaje de error contiene información sobre email inválido
    assert "email address" in response.json()["detail"]


def test_register_user_missing_required_fields(client, setup_test_db):
    # Intentar registrar un usuario sin campos requeridos
    response = client.post(
        "/api/v1/register",
        json={"email": "john@example.com", "password": "password123"},
    )
    assert response.status_code == 422
    # Verificar que el mensaje de error contiene información sobre campo requerido
    assert "Field required" in response.json()["detail"]
    # También podemos verificar que la respuesta es del formato Problem+JSON
    assert "type" in response.json()
    assert "title" in response.json()
    assert "status" in response.json()


def test_register_user_short_password(client, setup_test_db):
    # Intentar registrar un usuario con contraseña corta
    response = client.post(
        "/api/v1/register",
        json={"name": "John Doe", "email": "john@example.com", "password": "123"},
    )
    assert response.status_code == 422
    # Verificar que el mensaje contiene información sobre la longitud de la contraseña
    assert "contraseña debe tener al menos 6 caracteres" in response.json()["detail"]


def test_register_user_non_alphanumeric_password(client, setup_test_db):
    # Intentar registrar un usuario con contraseña no alfanumérica
    response = client.post(
        "/api/v1/register",
        json={"name": "John Doe", "email": "john@example.com", "password": "pass@123"},
    )
    assert response.status_code == 422
    # Verificar que el mensaje contiene información sobre caracteres alfanuméricos
    assert "contraseña debe ser alfanumérica" in response.json()["detail"]


def test_register_user_name_with_special_characters(client, setup_test_db):
    # Intentar registrar un usuario con un nombre que contiene caracteres especiales
    response = client.post(
        "/api/v1/register",
        json={
            "name": "John@Doe!",
            "email": "john@example.com",
            "password": "password123",
        },
    )
    assert response.status_code == 422
    # Verificar que el mensaje contiene información sobre caracteres especiales en el nombre
    assert "nombre no puede contener caracteres especiales" in response.json()["detail"]


def test_register_teacher_user(client, setup_test_db):
    # Registrar un usuario como profesor
    response = client.post(
        "/api/v1/register",
        json={
            "name": "John Teacher",
            "email": "teacher@example.com",
            "password": "password123",
            "location": "Buenos Aires",
            "is_teacher": True,
        },
    )
    assert response.status_code == 200
    assert response.json()["status"] == "success"
    assert response.json()["data"]["is_teacher"] is True


def test_register_student_user(client, setup_test_db):
    # Registrar un usuario como estudiante (default)
    response = client.post(
        "/api/v1/register",
        json={
            "name": "John Student",
            "email": "student@example.com",
            "password": "password123",
            "location": "Buenos Aires",
        },
    )
    assert response.status_code == 200
    assert response.json()["status"] == "success"
    assert response.json()["data"]["is_teacher"] is False
