from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.schemas.user import UserCreate, UserLogin, Token, CurrentUser, User, UserUpdate
from app.controllers.user_controller import (
    handle_register_user,
    handle_login_user,
    handle_get_users,
    handle_get_user,
    handle_edit_user,
    handle_delete_user,
)
from app.core.security import get_current_active_user
from app.db.dependencies import get_db
from typing import Annotated, List
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import ValidationError
import logging
import traceback

router = APIRouter()


@router.post("/register", response_model=dict)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    try:
        user_data = handle_register_user(db, user)
        return {
            "status": "success",
            "data": {
                "id": user_data.id,
                "name": user_data.name,
                "email": user_data.email,
                "location": user_data.location,
                "is_teacher": user_data.is_teacher,
                "academic_level": user_data.academic_level,
            },
        }
    except HTTPException as e:
        logging.error(f"HTTPException en register_user: {e.detail}")
        raise e
    except Exception as e:
        logging.error(f"Exception en register_user: {str(e)}")
        logging.error(traceback.format_exc())
        raise HTTPException(
            status_code=500, detail=f"Error interno del servidor: {str(e)}"
        )


@router.get("/users", response_model=List[User])
async def get_users(
    current_user: Annotated[CurrentUser, Depends(get_current_active_user)],
    db: Session = Depends(get_db),
):
    """
    Obtener lista de todos los usuarios.
    Requiere autenticación.
    """
    try:
        return handle_get_users(db)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error interno del servidor: {str(e)}",
        )


@router.get("/user/{user_id}", response_model=User)
async def get_user(
    user_id: int,
    current_user: Annotated[CurrentUser, Depends(get_current_active_user)],
    db: Session = Depends(get_db),
):
    """
    Obtener información de un usuario específico por ID.
    Requiere autenticación.
    """
    try:
        return handle_get_user(db, user_id)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error interno del servidor: {str(e)}",
        )


@router.put("/edituser/{user_id}", response_model=User)
async def edit_user(
    user_id: int,
    user_data: UserUpdate,
    current_user: Annotated[CurrentUser, Depends(get_current_active_user)],
    db: Session = Depends(get_db),
):
    """
    Actualizar información de un usuario específico por ID.
    Requiere autenticación.
    """
    try:
        return handle_edit_user(db, user_id, user_data)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error interno del servidor: {str(e)}",
        )


@router.delete("/deleteuser/{user_id}", response_model=User)
async def delete_user(
    user_id: int,
    current_user: Annotated[CurrentUser, Depends(get_current_active_user)],
    db: Session = Depends(get_db),
):
    """
    Eliminar un usuario específico por ID.
    Requiere autenticación.
    """
    try:
        return handle_delete_user(db, user_id)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error interno del servidor: {str(e)}",
        )


@router.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_db),
):
    try:
        logging.info(f"Intento de login para usuario: {form_data.username}")
        credentials = UserLogin(email=form_data.username, password=form_data.password)
        return handle_login_user(db, credentials)

    except ValidationError as e:
        error_detail = "Formato de email o contraseña inválido"
        if hasattr(e, "errors") and e.errors():
            error_detail = "; ".join([err["msg"] for err in e.errors()])

        logging.error(f"Error de validación en login: {error_detail}")
        logging.error(traceback.format_exc())

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_detail,
        )

    except HTTPException:
        raise

    except Exception as e:
        logging.error(f"Exception no manejada en login: {str(e)}")
        logging.error(traceback.format_exc())

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor",
        )


@router.get("/users/me/", response_model=CurrentUser)
async def read_users_me(
    current_user: Annotated[CurrentUser, Depends(get_current_active_user)],
):
    try:
        return current_user

    except HTTPException as e:
        raise e

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error interno del servidor: {str(e)}"
        )
