from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel


class CreateOperacionDTO(BaseModel):
    cuenta_id: int
    activo_id: int
    tipo: str
    cantidad: Decimal
    precio_unitario: Decimal
    comision: Decimal
    total: Decimal
    estado: str


class OperacionResponseDTO(BaseModel):
    id: int
    cuenta_id: int
    activo_id: int
    tipo: str
    cantidad: Decimal
    precio_unitario: Decimal
    comision: Decimal
    total: Decimal
    fecha: datetime
    estado: str
    ganancia_realizada: Decimal | None = None

    model_config = {"from_attributes": True}
