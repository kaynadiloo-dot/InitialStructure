from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel


class CreateMovimientoDTO(BaseModel):
    cuenta_id: int
    tipo: str
    moneda: str
    monto: Decimal
    descripcion: str | None = None


class MovimientoResponseDTO(BaseModel):
    id: int
    cuenta_id: int
    tipo: str
    moneda: str
    monto: Decimal
    fecha: datetime
    descripcion: str | None

    model_config = {"from_attributes": True}
