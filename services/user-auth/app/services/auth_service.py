from sqlalchemy.orm import Session
from datetime import timedelta
from fastapi import HTTPException, status
from app.repositories.user_repository import get_user_by_email
from app.schemas.user import UserLogin, Token
from app.core.security import create_access_token
from app.core.config import settings


def authenticate_user(db: Session, email: str, password: str):
    user = get_user_by_email(db, email)
    if not user:
        return False
    # if not verify_password(password, user.hashed_password): # con hashed passw
    if not user.password == password:
        return False
    return user


def login_user(db: Session, credentials: UserLogin):
    try:
        user = authenticate_user(db, credentials.email, credentials.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.email}, expires_delta=access_token_expires
        )
        return Token(access_token=access_token, token_type="bearer")

    except HTTPException as e:
        raise e

    except Exception as e:
        raise HTTPException(status_code=500, detail="Error interno")
