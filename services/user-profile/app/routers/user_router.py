import traceback
from fastapi import APIRouter, HTTPException, status
from app.services.user_profile import handle_edit_user
from app.schemas.user import UserUpdate
import logging

router = APIRouter()


@router.put("/edituser")
async def edit_user(
    user_data: UserUpdate,
    user_id: int,
):
    try:
        logging.info("Intento de editar usuario")
        return await handle_edit_user(user_id, user_data)

    except HTTPException:
        raise

    except Exception as e:
        logging.error(f"Exception no manejada al editar usuario: {str(e)}")
        logging.error(traceback.format_exc())

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor",
        )
