from pydantic import BaseModel, Field

from src.schemas.inversiones_tipos import DecimalMonetario, IdPositivo


class CreateOperacionSchema(BaseModel):
    cuenta_id: IdPositivo
    activo_id: IdPositivo
    tipo: str = Field(min_length=1, max_length=30)
    cantidad: DecimalMonetario
    precio_unitario: DecimalMonetario
    comision: DecimalMonetario
    total: DecimalMonetario
    estado: str = Field(min_length=1, max_length=30)
