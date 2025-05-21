from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.repositories.user_repository import (
    create_user,
    get_all_users,
    get_user_by_id,
    update_user,
    delete_user,
    get_user_by_email,
)
from app.services.google_auth_service import validate_google_token
from app.core.metrics import metric_trace
from app.core.security import create_user_jwt
from app.schemas.user import UserCreate, UserUpdate, UserGoogleUpdate


@metric_trace("register_user")
def register_user(db: Session, user: UserCreate):
    try:
        return create_user(db, user)
    except HTTPException:
        raise
    except Exception:
        db.rollback()
        raise HTTPException(status_code=400, detail="El email ya está registrado")


@metric_trace("get_users")
def get_users(db: Session):
    try:
        return get_all_users(db)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error al obtener usuarios: {str(e)}"
        )


@metric_trace("get_user")
def get_user(db: Session, user_id: int):
    try:
        user = get_user_by_id(db, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        return user
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error al obtener usuario: {str(e)}"
        )


@metric_trace("edit_user")
def edit_user(db: Session, user_id: int, user_data: UserUpdate):
    try:
        return update_user(db, user_id, user_data)
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500, detail=f"Error al actualizar usuario: {str(e)}"
        )


@metric_trace("remove_user")
def remove_user(db: Session, user_id: int):
    try:
        return delete_user(db, user_id)
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500, detail=f"Error al eliminar usuario: {str(e)}"
        )


def link_google_account(db: Session, token: str):
    try:
        user_name, user_email = validate_google_token(token)
        google_user_data = UserGoogleUpdate(name=user_name, email=user_email)
        user = get_user_by_email(db, user_email)
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")

        update_user(db, user.id, google_user_data)

        return create_user_jwt(user_email)
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500, detail=f"Error al vincular cuenta de Google: {str(e)}"
        )
