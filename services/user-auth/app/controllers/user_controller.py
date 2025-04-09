from sqlalchemy.orm import Session
from app.services.user_service import register_user
from app.schemas.user import UserCreate


def handle_register_user(db: Session, user: UserCreate):
    return register_user(db, user)
