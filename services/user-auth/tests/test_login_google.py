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
from unittest.mock import patch, MagicMock

# Configurar logging para suprimir mensajes de FastAPI
logging.getLogger("uvicorn").setLevel(logging.WARNING)
logging.getLogger("fastapi").setLevel(logging.WARNING)

# Usar la URL de la base de datos de la variable de entorno si está disponible, o db como fallback
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


valid_user_name = "John Doe"
valid_user_email = "john@example.com"

valid_user_data = {
    "email": valid_user_email,
    "name": valid_user_name,
}


@patch(
    "app.services.google_auth_service.id_token.verify_oauth2_token",
    new_callable=MagicMock,
)
def test_login_success_user_not_registered_in_db(
    mock_verify_token, client, setup_test_db
):
    # Login google exitoso, Usuario no registrado en la base de datos
    mock_verify_token.return_value = (
        valid_user_data  # Mock de validación de google token
    )

    response = client.post(
        "/api/v1/token/google",
        headers={"Authorization": f"Bearer valid_token"},
    )

    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@patch(
    "app.services.google_auth_service.id_token.verify_oauth2_token",
    new_callable=MagicMock,
)
def test_login_success_user_registered_in_db_with_auth_provider_google(
    mock_verify_token, client, setup_test_db
):
    # Login google exitoso, Usuario ya registrado en la base de datos y con auth_provider google
    mock_verify_token.return_value = (
        valid_user_data  # Mock de validación de google token
    )

    # Registrar un usuario con auth_provider google
    from app.models.user import User, AuthProvider

    user = User(
        name=valid_user_name,  # Mismas credenciales que el mock
        email=valid_user_email,  # Mismas credenciales que el mock
        password="fake_passw",
        auth_provider=AuthProvider.GOOGLE,
    )
    db = TestingSessionLocal()
    db.add(user)
    db.commit()
    db.close()

    response = client.post(
        "/api/v1/token/google",
        headers={"Authorization": f"Bearer valid_token"},
    )

    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@patch(
    "app.services.google_auth_service.id_token.verify_oauth2_token",
    new_callable=MagicMock,
)
def test_login_success_user_registered_in_db_with_auth_provider_local(
    mock_verify_token, client, setup_test_db
):
    # Login google exitoso, Usuario ya registrado en la base de datos y sin auth_provider google
    mock_verify_token.return_value = (
        valid_user_data  # Mock de validación de google token
    )

    # Registro de aplicacion, auth_provider local
    client.post(
        "/api/v1/register",
        json={
            "name": valid_user_name,  # Valid user data
            "email": valid_user_email,  # Valid user data
            "password": "password123",
        },
    )

    response = client.post(
        "/api/v1/token/google",
        headers={"Authorization": f"Bearer valid_token"},
    )

    data = response.json()
    assert "sincronize" in data
    assert data["sincronize"] is True


@patch(
    "app.services.google_auth_service.id_token.verify_oauth2_token",
    new_callable=MagicMock,
)
def test_login_error_invalid_token(mock_verify_token, client, setup_test_db):
    # Login google fallido, token invalido
    mock_verify_token.side_effect = ValueError("Invalid token")

    response = client.post(
        "/api/v1/token/google",
        headers={"Authorization": f"Bearer valid_token"},
    )

    expect_error_response(response, 401)


@patch(
    "app.services.google_auth_service.id_token.verify_oauth2_token",
    new_callable=MagicMock,
)
@patch("app.services.google_auth_service.get_user_by_email")
def test_login_internal_error(mock_get_user, mock_verify_token, client, setup_test_db):
    # Login google fallido, token invalido
    mock_verify_token.return_value = valid_user_data
    mock_get_user.side_effect = Exception("Internal error")

    response = client.post(
        "/api/v1/token/google",
        headers={"Authorization": f"Bearer valid_token"},
    )

    expect_error_response(response, 500)


@patch(
    "app.services.google_auth_service.id_token.verify_oauth2_token",
    new_callable=MagicMock,
)
def test_login_success_user_registered_in_db_with_auth_provider_local_and_link(
    mock_verify_token, client, setup_test_db
):
    # Login google exitoso, Usuario ya registrado en la base de datos y sin auth_provider google
    mock_verify_token.return_value = (
        valid_user_data  # Mock de validación de google token
    )

    # Registro de aplicacion, auth_provider local
    client.post(
        "/api/v1/register",
        json={
            "name": valid_user_name,  # Valid user data
            "email": valid_user_email,  # Valid user data
            "password": "password123",
        },
    )

    response = client.post(
        "/api/v1/token/google",
        headers={"Authorization": f"Bearer valid_token"},
    )

    data = response.json()
    assert "sincronize" in data
    assert data["sincronize"] is True

    link_response = client.post(
        "/api/v1/token/google/link",
        headers={"Authorization": f"Bearer valid_token"},
        json={
            "name": valid_user_name,
            "password": "password123",
        },
    )

    data = link_response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
