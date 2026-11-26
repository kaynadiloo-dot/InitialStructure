from pydantic import BaseModel, Field

from src.schemas.inversiones_tipos import DecimalMonetario, IdPositivo


class CreateMovimientoSchema(BaseModel):
    cuenta_id: IdPositivo
    tipo: str = Field(min_length=1, max_length=30)
    moneda: str = Field(min_length=1, max_length=3)
    monto: DecimalMonetario
    descripcion: str | None = Field(default=None, max_length=200)
