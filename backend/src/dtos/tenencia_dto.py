from decimal import Decimal

from pydantic import BaseModel


class CreateTenenciaDTO(BaseModel):
    cuenta_id: int
    activo_id: int
    cantidad: Decimal
    precio_promedio: Decimal


class UpdateTenenciaDTO(BaseModel):
    cantidad: Decimal
    precio_promedio: Decimal


class TenenciaResponseDTO(BaseModel):
    cuenta_id: int
    activo_id: int
    cantidad: Decimal
    precio_promedio: Decimal

    model_config = {"from_attributes": True}
