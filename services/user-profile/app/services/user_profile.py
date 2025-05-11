from app.schemas.user import UserUpdate
from fastapi import HTTPException, status
from app.repositories.user_repository import edit_user
import logging


async def handle_edit_user(user_id: int, user_data: UserUpdate):
    try:
        return await edit_user(user_id, user_data)
    except HTTPException as e:
        raise e

    except Exception as e:
        logging.error(f"Error no controlado en editar usuario: {str(e)}")
        # Errores no esperados
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}",
        )
