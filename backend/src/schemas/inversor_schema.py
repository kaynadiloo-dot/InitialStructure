from typing import Literal

from pydantic import BaseModel, EmailStr, Field, field_validator

from src.schemas.inversiones_tipos import Cuit


PerfilRiesgo = Literal["conservador", "moderado", "agresivo"]


class CreateInversorSchema(BaseModel):
    email: EmailStr
    nombre: str = Field(min_length=1, max_length=100)
    cuit: Cuit
    perfil_riesgo: PerfilRiesgo

    @field_validator("email")
    @classmethod
    def normalizar_email(cls, email: str) -> str:
        return email.lower()


class PerfilRiesgoSchema(BaseModel):
    perfil_riesgo: PerfilRiesgo
