from pydantic import BaseModel, EmailStr, field_validator, ConfigDict
from app.models.user import AuthProvider
from typing import Literal, Union
from datetime import datetime
import re
import unicodedata


class UserBase(BaseModel):
    name: str
    email: EmailStr
    location: str | None = None
    is_teacher: bool = False
    academic_level: int = 0

    @field_validator("name")
    @classmethod
    def validate_name(cls, v):
        if not all(c.isalpha() or c.isspace() for c in v):
            raise ValueError("El nombre solo puede contener letras y espacios.")
        return v


class UserCreate(UserBase):
    password: str

    @field_validator("password")
    @classmethod
    def validate_password(cls, v):
        if len(v) < 6:
            raise ValueError("La contraseña debe tener al menos 6 caracteres.")
        if not v.isalnum():
            raise ValueError("La contraseña debe ser alfanumérica.")
        return v


class UserCreateGoogle(UserBase):
    auth_provider: Literal[AuthProvider.GOOGLE] = AuthProvider.GOOGLE
    password: str


class UserUpdate(BaseModel):
    name: str | None = None
    email: EmailStr | None = None
    password: str | None = None
    location: str | None = None
    is_teacher: bool | None = None
    academic_level: int | None = None
    is_blocked: bool | None = None
    auth_provider: AuthProvider | None = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, v):
        if not all(c.isalpha() or c.isspace() for c in v):
            raise ValueError("El nombre solo puede contener letras y espacios.")
        return v

    @field_validator("password")
    @classmethod
    def validate_password(cls, v):
        if v is not None:
            if len(v) < 6:
                raise ValueError("La contraseña debe tener al menos 6 caracteres.")
            if not v.isalnum():
                raise ValueError("La contraseña debe ser alfanumérica.")
        return v

class UserGoogleUpdate(UserUpdate):
    auth_provider: Literal[AuthProvider.LOCAL_GOOGLE] = AuthProvider.LOCAL_GOOGLE


class User(UserBase):
    id: int
    is_blocked: bool
    failed_login_attempts: int
    first_login_failure: datetime | None
    blocked_until: datetime | None

    model_config = ConfigDict(from_attributes=True)


class UserLogin(BaseModel):
    email: EmailStr
    password: str

    @field_validator("password")
    @classmethod
    def validate_password(cls, v):
        if not v:
            raise ValueError("La contraseña no puede estar vacía.")
        if len(v) < 6:
            raise ValueError("La contraseña debe tener al menos 6 caracteres.")
        if not v.isalnum():
            raise ValueError("La contraseña debe ser alfanumérica.")
        return v


class ServiceLogin(BaseModel):
    user: str
    password: str


class CurrentUser(BaseModel):
    id: int
    email: EmailStr
    name: str
    is_teacher: bool = False
    location: str | None = None


class UserInDB(CurrentUser):
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None
    scopes: list[str] = []


class CurrentService(BaseModel):
    name: str


class Identity(BaseModel):
    role: Literal["user", "service"]
    identity: Union[CurrentUser, CurrentService]
