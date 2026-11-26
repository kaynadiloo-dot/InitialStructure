from datetime import date
from decimal import Decimal

from pydantic import BaseModel


class CreateDividendoDTO(BaseModel):
    activo_id: int
    monto_por_unidad: Decimal
    fecha_pago: date


class DividendoResponseDTO(BaseModel):
    id: int
    activo_id: int
    monto_por_unidad: Decimal
    fecha_pago: date

    model_config = {"from_attributes": True}
