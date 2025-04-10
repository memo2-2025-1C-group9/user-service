from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.repositories.user_repository import create_user
from app.schemas.user import UserCreate


def register_user(db: Session, user: UserCreate):
    try:
        return create_user(db, user)
    except Exception:
        db.rollback()
        raise HTTPException(status_code=400, detail="El email ya está registrado")
