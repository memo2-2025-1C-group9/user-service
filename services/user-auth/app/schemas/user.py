from pydantic import BaseModel, EmailStr, field_validator
import re


class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str

    @field_validator("password")
    def validate_password(cls, password):
        if len(password) < 6:
            raise ValueError("La contraseña debe tener al menos 6 caracteres.")
        if not password.isalnum():
            raise ValueError("La contraseña debe ser alfanumérica.")
        return password

    @field_validator("name")
    def validate_name(cls, name):
        if not re.match("^[a-zA-Z0-9 ]+$", name):
            raise ValueError("El nombre no puede contener caracteres especiales.")
        return name
