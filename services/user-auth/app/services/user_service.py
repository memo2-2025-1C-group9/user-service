from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.repositories.user_repository import (
    create_user,
    get_all_users,
    get_user_by_id,
    update_user,
    delete_user,
)
from app.schemas.user import UserCreate, UserUpdate


def register_user(db: Session, user: UserCreate):
    try:
        return create_user(db, user)
    except HTTPException:
        raise
    except Exception:
        db.rollback()
        raise HTTPException(status_code=400, detail="El email ya está registrado")


def get_users(db: Session):
    try:
        return get_all_users(db)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error al obtener usuarios: {str(e)}"
        )


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
