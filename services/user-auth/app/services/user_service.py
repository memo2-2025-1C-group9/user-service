from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.repositories.user_repository import (
    create_user,
    get_all_users,
    get_user_by_id,
    update_user,
    delete_user,
)
from app.core.metrics import send_metric
from app.schemas.user import UserCreate, UserUpdate


def register_user(db: Session, user: UserCreate):
    try:
        send_metric("user_service.register_attempt")
        user = create_user(db, user)
        send_metric("user_service.register_success")
        return user
    except HTTPException:
        send_metric("user_service.register_error")
        raise
    except Exception:
        send_metric("user_service.register_error")
        db.rollback()
        raise HTTPException(status_code=400, detail="El email ya está registrado")


def get_users(db: Session):
    try:
        send_metric("user_service.get_users_attempt")
        users = get_all_users(db)
        send_metric("user_service.get_users_success")
        return users
    except Exception as e:
        send_metric("user_service.get_users_error")
        raise HTTPException(
            status_code=500, detail=f"Error al obtener usuarios: {str(e)}"
        )


def get_user(db: Session, user_id: int):
    try:
        send_metric("user_service.get_user_attempt")
        user = get_user_by_id(db, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        send_metric("user_service.get_user_success")
        return user
    except HTTPException:
        send_metric("user_service.get_user_error")
        raise
    except Exception as e:
        send_metric("user_service.get_user_error")
        raise HTTPException(
            status_code=500, detail=f"Error al obtener usuario: {str(e)}"
        )


def edit_user(db: Session, user_id: int, user_data: UserUpdate):
    try:
        send_metric("user_service.edit_user_attempt")
        user = update_user(db, user_id, user_data)
        send_metric("user_service.edit_user_success")
        return user
    except HTTPException:
        send_metric("user_service.edit_user_error")
        raise
    except Exception as e:
        send_metric("user_service.edit_user_error")
        db.rollback()
        raise HTTPException(
            status_code=500, detail=f"Error al actualizar usuario: {str(e)}"
        )


def remove_user(db: Session, user_id: int):
    try:
        send_metric("user_service.remove_user_attempt")
        user = delete_user(db, user_id)
        send_metric("user_service.remove_user_success")
        return user
    except HTTPException:
        send_metric("user_service.remove_user_error")
        raise
    except Exception as e:
        send_metric("user_service.remove_user_error")
        db.rollback()
        raise HTTPException(
            status_code=500, detail=f"Error al eliminar usuario: {str(e)}"
        )
