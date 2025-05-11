from fastapi.testclient import TestClient
from app.main import app
from unittest.mock import patch, AsyncMock

client = TestClient(app)

valid_user_data = {"name": "new username", "location": "New location"}


def expect_error_response(response, status_code: int):
    assert response.status_code == status_code
    data = response.json()
    assert "type" in data
    assert "title" in data
    assert "status" in data
    assert "detail" in data
    assert "instance" in data


@patch("app.services.user_profile.edit_user", new_callable=AsyncMock)
def test_edit_user_success(mock_edit):
    """Prueba exitosa para editar un usuario"""
    mock_edit.return_value = valid_user_data

    response = client.put(
        "/edituser",
        json=valid_user_data,
        params={"user_id": 7},
    )

    assert response.status_code == 200
    assert response.json() == valid_user_data


@patch("app.services.user_profile.edit_user", new_callable=AsyncMock)
def test_edit_user_unexpected_exception(mock_edit):
    mock_edit.side_effect = Exception("Unexpected error")

    response = client.put(
        "/edituser",
        json=valid_user_data,
        params={"user_id": 7},
    )

    expect_error_response(response, 500)


@patch("app.services.user_profile.edit_user", new_callable=AsyncMock)
def test_body_with_name_only(mock_edit):
    mock_edit.return_value = {"name": "Pepe"}
    response = client.put("/edituser", json={"name": "Pepe"}, params={"user_id": 1})
    assert response.status_code == 200
    assert response.json() == {"name": "Pepe"}


@patch("app.services.user_profile.edit_user", new_callable=AsyncMock)
def test_body_with_location_only(mock_edit):
    mock_edit.return_value = {"location": "Buenos Aires"}
    response = client.put(
        "/edituser", json={"location": "Buenos Aires"}, params={"user_id": 1}
    )
    assert response.status_code == 200
    assert response.json() == {"location": "Buenos Aires"}


def test_empty_body():
    response = client.put("/edituser", json={}, params={"user_id": 1})
    expect_error_response(response, 422)


def test_missing_body():
    response = client.put("/edituser", params={"user_id": 1})
    expect_error_response(response, 422)


def test_empty_name():
    response = client.put("/edituser", json={"name": ""}, params={"user_id": 1})
    expect_error_response(response, 422)


def test_empty_location():
    response = client.put("/edituser", json={"location": ""}, params={"user_id": 1})
    expect_error_response(response, 422)
