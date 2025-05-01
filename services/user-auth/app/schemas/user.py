from pydantic import BaseModel, EmailStr, field_validator, ConfigDict
from datetime import datetime
import re


class UserBase(BaseModel):
    name: str
    email: EmailStr
    location: str | None = None
    is_teacher: bool = False
    academic_level: int = 0

    @field_validator("name")
    @classmethod
    def validate_name(cls, v):
        if not re.match(r"^[a-zA-Z\s]+$", v):
            raise ValueError("El nombre no puede contener caracteres especiales.")
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


class UserUpdate(BaseModel):
    name: str | None = None
    email: EmailStr | None = None
    password: str | None = None
    location: str | None = None
    is_teacher: bool | None = None
    academic_level: int | None = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, v):
        if v is not None and not re.match(r"^[a-zA-Z\s]+$", v):
            raise ValueError("El nombre no puede contener caracteres especiales.")
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



class CurrentUser(UserBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


class UserInDB(CurrentUser):
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: str | None = None
