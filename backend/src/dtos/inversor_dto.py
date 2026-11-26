from datetime import datetime

from pydantic import BaseModel


class CreateInversorDTO(BaseModel):
    email: str
    nombre: str
    cuit: str
    perfil_riesgo: str


class InversorResponseDTO(BaseModel):
    id: int
    email: str
    nombre: str
    cuit: str
    perfil_riesgo: str
    fecha_alta: datetime

    model_config = {"from_attributes": True}
