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
) -> Token:
    try:
        # Validar formato básico del email
        if not "@" in form_data.username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid email format"
            )

        credentials = UserLogin(email=form_data.username, password=form_data.password)
        return handle_login_user(db, credentials)
    except HTTPException as e:
        # Si ya es una HTTPException, la propagamos tal cual
        raise e
    except ValidationError as e:
        # Si hay un error de validación, lo transformamos a 400
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        # Para cualquier otro error, lo transformamos a 401
        print(f"Error en login: {str(e)}")  # Para debug
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"}
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
