from sqlalchemy.orm import Session
from app.services.user_service import (
    register_user,
    get_users,
    get_user,
    edit_user,
    remove_user,
)
from app.services.auth_service import login_user
from app.schemas.user import UserCreate, UserLogin, UserUpdate


def handle_register_user(db: Session, user: UserCreate):
    return register_user(db, user)


def handle_login_user(db: Session, user: UserLogin):
    return login_user(db, user)


def handle_get_users(db: Session):
    return get_users(db)


def handle_get_user(db: Session, user_id: int):
    return get_user(db, user_id)


def handle_edit_user(db: Session, user_id: int, user_data: UserUpdate):
    return edit_user(db, user_id, user_data)


def handle_delete_user(db: Session, user_id: int):
    return remove_user(db, user_id)
