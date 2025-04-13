from pydantic import BaseModel, EmailStr, field_validator, ConfigDict
import re


class UserBase(BaseModel):
    name: str
    email: EmailStr
    location: str | None = None

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


class User(UserBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class UserLogin(BaseModel):
    email: EmailStr
    password: str

    @field_validator("password")
    @classmethod
    def validate_password(cls, v):
        if len(v) < 6:
            raise ValueError("La contraseña debe tener al menos 6 caracteres.")
        if not v.isalnum():
            raise ValueError("La contraseña debe ser alfanumérica.")
        return v


class CurrentUser(BaseModel):
    email: EmailStr
    name: str


class UserInDB(CurrentUser):
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: str | None = None
