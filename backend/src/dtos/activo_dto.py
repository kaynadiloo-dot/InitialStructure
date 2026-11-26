from decimal import Decimal

from pydantic import BaseModel


class CreateActivoDTO(BaseModel):
    ticker: str
    nombre: str
    tipo: str
    moneda: str
    precio_actual: Decimal
    nivel_riesgo: int
    activo: bool = True


class ActivoResponseDTO(BaseModel):
    id: int
    ticker: str
    nombre: str
    tipo: str
    moneda: str
    precio_actual: Decimal
    nivel_riesgo: int
    activo: bool

    model_config = {"from_attributes": True}
