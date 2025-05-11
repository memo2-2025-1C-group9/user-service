from fastapi import HTTPException, status
from app.core.auth import get_service_auth
from app.core.config import settings
import httpx
import logging


async def edit_user(user_id, user_data, retry=True):
    url = f"{settings.AUTH_SERVICE_URL}/edituser/{user_id}"

    auth_service = get_service_auth()
    access_token = auth_service.get_token()

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    try:
        # Realizar la solicitud PUT al user-service
        logging.info(f"Enviando datos para actualizar el perfil del usuario: {user_id}")
        payload = user_data.model_dump(exclude_none=True)
        async with httpx.AsyncClient() as client:
            response = await client.put(url, json=payload, headers=headers)

        # Verificar si la respuesta es exitosa
        if response.status_code == 200:
            logging.info(f"Perfil del usuario actualizado correctamente (ID {user_id})")
            return response.json()
        else:
            if response.status_code == 401 and retry:
                logging.warning("Token expirado o inválido, intentando renovar...")
                await auth_service.login()
                return await edit_user(user_id, user_data, retry=False)
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Error al actualizar el perfil del usuario (ID {user_id})",
            )
    except HTTPException as e:
        raise e

    except Exception as e:
        logging.error(f"Error no controlado en editar usuario: {str(e)}")
        # Errores no esperados
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}",
        )
