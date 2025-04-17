from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.schemas.user import UserCreate, UserLogin, Token, CurrentUser
from app.controllers.user_controller import handle_register_user, handle_login_user
from app.core.security import get_current_active_user
from app.db.dependencies import get_db
from typing import Annotated
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import ValidationError

router = APIRouter()


@router.post("/register")
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
            },
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error interno del servidor: {str(e)}"
        )


@router.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_db),
):
    try:
        credentials = UserLogin(email=form_data.username, password=form_data.password)
        return handle_login_user(db, credentials)

    except ValidationError as e:
        # Error en la validación de los datos de entrada
        error_detail = "Formato de email o contraseña inválido"
        if hasattr(e, "errors") and e.errors():
            error_detail = "; ".join([err["msg"] for err in e.errors()])

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_detail,
        )

    except HTTPException as e:
        # Reenvía la excepción HTTP pero con el formato que queremos
        raise HTTPException(
            status_code=e.status_code,
            detail=e.detail,
            headers=e.headers if hasattr(e, "headers") else None,
        )

    except Exception as e:
        # Para cualquier otra excepción, devolvemos un error 500 con mensaje genérico
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
