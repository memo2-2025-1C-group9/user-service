from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.schemas.user import UserCreate, UserLogin, Token
from app.controllers.user_controller import handle_register_user, handle_login_user

from typing import Annotated
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import ValidationError

router = APIRouter()


def get_db():
    db = None
    try:
        db = SessionLocal()
        yield db
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error de conexión a la base de datos: {str(e)}"
        )
    finally:
        if db:
            try:
                db.close()
            except Exception as e:
                raise HTTPException(
                    status_code=500, detail=f"Error al cerrar la conexión: {str(e)}"
                )


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
        credentials = UserLogin(email=form_data.username, password=form_data.password)
        return handle_login_user(db, credentials)

    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid input email or password",
        )

    except HTTPException as e:
        raise e

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error interno del servidor: {str(e)}"
        )
