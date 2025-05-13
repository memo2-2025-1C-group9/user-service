import jwt
from typing import Annotated
from datetime import datetime, timedelta, timezone

from pydantic import ValidationError
from app.schemas.user import CurrentService, Identity, UserInDB, TokenData, CurrentUser
from app.core.config import settings
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status
from jwt.exceptions import InvalidTokenError
from fastapi.security import OAuth2PasswordBearer, SecurityScopes
from app.db.dependencies import get_db
from app.repositories.user_repository import get_user_by_email
from app.schemas.user import Token

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="token",
    scopes={
        "user": "Acceso como usuario registrado (alumno o docente)",
        "service": "Acceso completo como servicio",
    },
)


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def create_service_jwt(service_name: str) -> Token:
    access_token_expires = timedelta(
        minutes=settings.SERVICE_ACCESS_TOKEN_EXPIRE_MINUTES
    )
    access_token = create_access_token(
        data={
            "sub": service_name,
            "scopes": ["service"],
            "role": "service",
        },
        expires_delta=access_token_expires,
    )
    return Token(access_token=access_token, token_type="bearer")


def create_user_jwt(user_email: str) -> Token:
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "sub": user_email,
            "scopes": ["user"],
            "role": "user",
        },
        expires_delta=access_token_expires,
    )
    return Token(access_token=access_token, token_type="bearer")


def get_user(db, email: str):
    user = get_user_by_email(db, email=email)
    if user:
        return UserInDB(**user.__dict__)
    return None


def create_credentials_exception():
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )


async def get_current_identity(
    security_scopes: SecurityScopes,
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Session = Depends(get_db),
):
    if security_scopes.scopes:
        authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
    else:
        authenticate_value = "Bearer"

    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )

        username = payload.get("sub")
        if username is None:
            raise create_credentials_exception()

        token_scopes = payload.get("scopes", [])
        token_data = TokenData(scopes=token_scopes, username=username)
    except (InvalidTokenError, ValidationError):
        raise create_credentials_exception()

    role = payload.get("role")
    if role == "service":
        user = Identity(role=role, identity=CurrentService(name=username))
    elif role == "user":
        current_user = get_user(db, email=token_data.username)
        user = Identity(role=role, identity=CurrentUser(**current_user.__dict__))

    if user is None:
        raise create_credentials_exception()
    for scope in token_data.scopes:
        if scope not in security_scopes.scopes:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not enough permissions",
                headers={"WWW-Authenticate": authenticate_value},
            )

    return user


async def get_current_active_user(
    current_user: Annotated[CurrentUser, Depends(get_current_identity)],
):
    return current_user
