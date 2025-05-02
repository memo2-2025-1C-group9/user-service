from pydantic import BaseModel, field_validator
import re


class UserUpdate(BaseModel):
    name: str | None = None
    location: str | None = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, v):
        if v is not None and not re.match(r"^[a-zA-Z\s]+$", v):
            raise ValueError("El nombre no puede contener caracteres especiales.")
        return v

    class Config:
        extra = "forbid"  # No se permiten campos adicionales
