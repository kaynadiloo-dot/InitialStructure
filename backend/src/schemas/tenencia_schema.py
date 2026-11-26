from pydantic import BaseModel

from src.schemas.inversiones_tipos import DecimalMonetario, IdPositivo


class CreateTenenciaSchema(BaseModel):
    cuenta_id: IdPositivo
    activo_id: IdPositivo
    cantidad: DecimalMonetario
    precio_promedio: DecimalMonetario


class UpdateTenenciaSchema(BaseModel):
    cantidad: DecimalMonetario
    precio_promedio: DecimalMonetario
