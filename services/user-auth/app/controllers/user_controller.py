from sqlalchemy.orm import Session
from app.services.user_service import register_user
from app.services.auth_service import login_user
from app.schemas.user import UserCreate, UserLogin


def handle_register_user(db: Session, user: UserCreate):
    return register_user(db, user)


def handle_login_user(db: Session, user: UserLogin):
    return login_user(db, user)
