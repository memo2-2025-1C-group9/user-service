from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.user import User
from app.schemas.user import UserCreate
from fastapi import HTTPException, status


def get_user_by_email(db: Session, email: str) -> User | None:
    return db.scalar(select(User).where(User.email == email))


def create_user(db: Session, user_data: UserCreate):
    # Verificar si el email ya existe
    existing_user = get_user_by_email(db, user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El email ya está registrado",
        )

    new_user = User(
        name=user_data.name,
        email=user_data.email,
        password=user_data.password,
        location=user_data.location,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user
