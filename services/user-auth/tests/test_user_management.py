import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app, Base
from app.routers.user_router import get_db
from app.models.user import User
import os

# Usar la URL de la base de datos desde las variables de entorno
TEST_DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}?sslmode=require",
)

engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture(scope="function")
def setup_test_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def register_and_login_user(
    client,
    name="Test User",
    email="test@example.com",
    password="password123",
    location=None,
    is_teacher=False,
):
    # Register user with all fields
    register_data = {
        "name": name,
        "email": email,
        "password": password,
        "location": location,
        "is_teacher": is_teacher,
    }
    # Remove None values
    register_data = {k: v for k, v in register_data.items() if v is not None}

    client.post("/api/v1/register", json=register_data)

    # Login and get token
    response = client.post(
        "/api/v1/token",
        data={"username": email, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    return response.json()["access_token"]


def test_get_all_users(client, setup_test_db):
    # Registrar y login con un usuario
    token = register_and_login_user(client)

    # Intentar obtener la lista de usuarios
    response = client.get("/api/v1/users", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    users = response.json()
    assert isinstance(users, list)
    assert len(users) == 1
    assert users[0]["email"] == "test@example.com"


def test_get_user_by_id(client, setup_test_db):
    # Registrar y login con un usuario
    token = register_and_login_user(client)

    # Obtener usuario por ID 1 (el primer usuario registrado)
    response = client.get(
        "/api/v1/user/1", headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    user = response.json()
    assert user["id"] == 1
    assert user["email"] == "test@example.com"


def test_get_nonexistent_user(client, setup_test_db):
    # Registrar y login con un usuario
    token = register_and_login_user(client)

    # Intentar obtener un usuario que no existe
    response = client.get(
        "/api/v1/user/999", headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Usuario no encontrado"


def test_edit_user(client, setup_test_db):
    # Registrar y login con un usuario
    token = register_and_login_user(client)

    # Editar el usuario
    response = client.put(
        "/api/v1/edituser/1",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name": "Updated Name",
            "location": "Updated Location",
            "academic_level": 2,
        },
    )

    assert response.status_code == 200
    user = response.json()
    assert user["name"] == "Updated Name"
    assert user["location"] == "Updated Location"
    assert user["academic_level"] == 2
    assert user["email"] == "test@example.com"  # El email no debería cambiar


def test_edit_nonexistent_user(client, setup_test_db):
    # Registrar y login con un usuario
    token = register_and_login_user(client)

    # Intentar editar un usuario que no existe
    response = client.put(
        "/api/v1/edituser/999",
        headers={"Authorization": f"Bearer {token}"},
        json={"name": "Updated Name"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Usuario no encontrado"


def test_delete_user(client, setup_test_db):
    # Registrar y login con un usuario que será eliminado
    token = register_and_login_user(client)

    # Registrar y login con un segundo usuario para verificar el borrado
    second_token = register_and_login_user(
        client, name="Second User", email="second@example.com", password="password123"
    )

    # Eliminar el primer usuario
    response = client.delete(
        "/api/v1/deleteuser/1", headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    deleted_user = response.json()
    assert deleted_user["id"] == 1
    assert deleted_user["email"] == "test@example.com"

    # Verificar que el usuario ya no existe usando el token del segundo usuario
    response = client.get(
        "/api/v1/user/1", headers={"Authorization": f"Bearer {second_token}"}
    )
    assert response.status_code == 404


def test_delete_nonexistent_user(client, setup_test_db):
    # Registrar y login con un usuario
    token = register_and_login_user(client)

    # Intentar eliminar un usuario que no existe
    response = client.delete(
        "/api/v1/deleteuser/999", headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Usuario no encontrado"


def test_unauthorized_access(client, setup_test_db):
    # Intentar acceder sin token
    endpoints = [
        ("/api/v1/users", "GET"),
        ("/api/v1/user/1", "GET"),
        ("/api/v1/edituser/1", "PUT"),
        ("/api/v1/deleteuser/1", "DELETE"),
    ]

    for endpoint, method in endpoints:
        if method == "GET":
            response = client.get(endpoint)
        elif method == "PUT":
            response = client.put(endpoint, json={"name": "Test"})
        else:
            response = client.delete(endpoint)

        assert response.status_code == 401
        assert "Not authenticated" in response.json()["detail"]


def test_read_users_me(client, setup_test_db):
    # Register and login with a user that has location and is_teacher set
    token = register_and_login_user(
        client,
        name="Test Teacher",
        email="teacher@example.com",
        password="password123",
        location="Buenos Aires",
        is_teacher=True,
    )

    # Get current user info
    response = client.get(
        "/api/v1/users/me/", headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    user = response.json()
    assert user["email"] == "teacher@example.com"
    assert user["name"] == "Test Teacher"
    assert user["location"] == "Buenos Aires"
    assert user["is_teacher"] is True
