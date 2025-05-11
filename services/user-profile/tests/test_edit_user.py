import pytest
from unittest.mock import AsyncMock, patch
from fastapi import HTTPException
from app.services.user_profile import edit_user
from app.schemas.user import UserUpdate


@pytest.mark.asyncio
async def test_edit_user_success():
    """Test para el caso exitoso de editar un usuario."""
    mock_token = "test-token"
    mock_response = {"name": "Nuevo Nombre"}

    with patch("app.core.auth.get_service_auth") as mock_auth, patch(
        "httpx.AsyncClient.put"
    ) as mock_put:
        mock_auth_instance = AsyncMock()
        mock_auth_instance.get_token.return_value = mock_token
        mock_auth.return_value = mock_auth_instance

        mock_response_obj = AsyncMock()
        mock_response_obj.status_code = 200
        mock_response_obj.json.return_value = mock_response
        mock_put.return_value = mock_response_obj

        data = UserUpdate(name="Nuevo Nombre")
        result = await edit_user(user_id=1, user_data=data)

        assert await result == mock_response


@pytest.mark.asyncio
async def test_edit_user_token_expired_then_success():
    """Test para el caso donde el token expira y luego se renueva correctamente."""
    mock_token = "expired-token"
    mock_new_token = "new-token"
    mock_response = {"name": "Nuevo Nombre"}

    with patch("app.core.auth.get_service_auth") as mock_auth, patch(
        "httpx.AsyncClient.put", new_callable=AsyncMock
    ) as mock_put:
        mock_auth_instance = AsyncMock()
        mock_auth_instance.get_token.side_effect = [mock_token, mock_new_token]
        mock_auth_instance.login.return_value = AsyncMock()
        mock_auth.return_value = mock_auth_instance

        # Respuestas simuladas
        expired_response = AsyncMock(status_code=401, text="Token expirado")
        success_response = AsyncMock(status_code=200)
        success_response.json.return_value = mock_response
        mock_put.side_effect = [expired_response, success_response]

        data = UserUpdate(name="Retry Test")
        result = await edit_user(user_id=1, user_data=data)

        assert await result == mock_response


@pytest.mark.asyncio
async def test_edit_user_token_expired_then_fails():
    """Test para el caso donde el token expira y la segunda llamada falla."""
    with patch("app.core.auth.get_service_auth") as mock_auth, patch(
        "httpx.AsyncClient.put", new_callable=AsyncMock
    ) as mock_put:
        mock_auth_instance = AsyncMock()
        mock_auth_instance.get_token.side_effect = ["expired-token", "still-invalid"]
        mock_auth_instance.login.return_value = AsyncMock()
        mock_auth.return_value = mock_auth_instance

        # Ambas respuestas con 401
        expired_response = AsyncMock(status_code=401, text="Token aún inválido")
        mock_put.side_effect = [expired_response, expired_response]

        data = UserUpdate(name="Retry Test Again")

        with pytest.raises(HTTPException) as exc_info:
            await edit_user(user_id=2, user_data=data)

        assert exc_info.value.status_code == 401


@pytest.mark.asyncio
async def test_edit_user_external_service_error():
    """Test para manejar errores del servicio externo"""
    with patch("app.core.auth.get_service_auth") as mock_auth, patch(
        "httpx.AsyncClient.put", new_callable=AsyncMock
    ) as mock_put:
        mock_auth_instance = AsyncMock()
        mock_auth_instance.get_token.return_value = "token"
        mock_auth.return_value = mock_auth_instance

        error_response = AsyncMock(status_code=404, text="Not Found")
        mock_put.return_value = error_response

        data = UserUpdate(name="Not Found Case")

        with pytest.raises(HTTPException) as exc_info:
            await edit_user(user_id=3, user_data=data)

        assert exc_info.value.status_code == 404
