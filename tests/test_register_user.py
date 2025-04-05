import pytest
import os
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError
from sqlalchemy.sql import text
from app.main import app, Base
from app.routers.user_router import get_db

# Usar la URL de la base de datos de la variable de entorno si está disponible, o localhost como fallback
TEST_DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://user:password@localhost:5432/test_student_management"
)
engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def create_test_database():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except OperationalError:
        # Usar la misma URL base pero con la base de datos postgres
        root_url = TEST_DATABASE_URL.replace("/test_student_management", "/postgres")
        root_engine = create_engine(root_url)
        with root_engine.connect() as connection:
            connection.execution_options(isolation_level="AUTOCOMMIT").execute(
                text("CREATE DATABASE test_student_management")
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

client = TestClient(app)


@pytest.fixture(scope="function")
def setup_test_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def test_register_user(setup_test_db):
    # Registrar un usuario correctamente
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


def test_register_duplicate_user(setup_test_db):
    client.post(
        "/api/v1/register",
        json={
            "name": "John Doe",
            "email": "john@example.com",
            "password": "password123",
        },
    )

    # Intentar registrar el mismo usuario nuevamente
    response = client.post(
        "/api/v1/register",
        json={
            "name": "John Doe",
            "email": "john@example.com",
            "password": "password123",
        },
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "El correo electrónico ya está registrado."


def test_register_user_short_password(setup_test_db):
    # Intentar registrar un usuario con contraseña corta
    response = client.post(
        "/api/v1/register",
        json={"name": "John Doe", "email": "john@example.com", "password": "123"},
    )
    assert response.status_code == 422
    assert (
        response.json()["detail"][0]["msg"]
        == "Value error, La contraseña debe tener al menos 6 caracteres."
    )


def test_register_user_non_alphanumeric_password(setup_test_db):
    # Intentar registrar un usuario con contraseña no alfanumérica
    response = client.post(
        "/api/v1/register",
        json={"name": "John Doe", "email": "john@example.com", "password": "pass@123"},
    )
    assert response.status_code == 422
    assert (
        response.json()["detail"][0]["msg"]
        == "Value error, La contraseña debe ser alfanumérica."
    )


def test_register_user_missing_fields(setup_test_db):
    # Intentar registrar un usuario con campos faltantes
    response = client.post(
        "/api/v1/register", json={"name": "John Doe", "email": "john@example.com"}
    )
    assert response.status_code == 422
    assert response.json()["detail"][0]["msg"] == "Field required"
    assert response.json()["detail"][0]["loc"] == ["body", "password"]


def test_register_user_invalid_email(setup_test_db):
    # Intentar registrar un usuario con un correo electrónico inválido
    response = client.post(
        "/api/v1/register",
        json={"name": "John Doe", "email": "invalid-email", "password": "password123"},
    )
    assert response.status_code == 422
    assert (
        response.json()["detail"][0]["msg"]
        == "value is not a valid email address: An email address must have an @-sign."
    )
    assert response.json()["detail"][0]["loc"] == ["body", "email"]


def test_register_user_name_with_special_characters(setup_test_db):
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
    assert (
        response.json()["detail"][0]["msg"]
        == "Value error, El nombre no puede contener caracteres especiales."
    )
