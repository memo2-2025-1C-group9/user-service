from pydantic import BaseModel, field_validator, model_validator
import re


class UserUpdate(BaseModel):
    name: str | None = None
    location: str | None = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, v):
        if v is not None:
            v = v.strip()
            if len(v) <= 0:
                raise ValueError("El nombre no puede estar vacío.")
            if not re.match(r"^[a-zA-Z\s]+$", v):
                raise ValueError("El nombre no puede contener caracteres especiales.")
        return v

    @field_validator("location")
    @classmethod
    def validate_location(cls, v):
        if v is not None:
            v = v.strip()
            if len(v) <= 0:
                raise ValueError("La ubicación no puede estar vacía.")
        return v

    @model_validator(mode="after")
    def check_at_least_one_field(self):
        if self.name is None and self.location is None:
            raise ValueError("Se debe proporcionar al menos un campo para actualizar.")
        return self

    class Config:
        extra = "forbid"  # No se permiten campos adicionales
