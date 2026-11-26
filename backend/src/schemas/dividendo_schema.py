from datetime import date

from pydantic import BaseModel, Field

from src.schemas.inversiones_tipos import DecimalMonetario, IdPositivo


class CreateDividendoSchema(BaseModel):
    activo_id: IdPositivo
    monto_por_unidad: DecimalMonetario = Field(gt=0)
    fecha_pago: date
