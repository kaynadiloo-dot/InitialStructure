from typing import Annotated, Literal

from pydantic import BaseModel, Field, StringConstraints

from src.schemas.inversiones_tipos import DecimalMonetario

TipoActivo = Literal["accion", "cedear", "bono"]
Moneda = Literal["ARS", "USD"]


class CreateActivoSchema(BaseModel):
    ticker: Annotated[str, StringConstraints(strip_whitespace=True, to_upper=True, min_length=1, max_length=20)]
    nombre: str = Field(min_length=1, max_length=100)
    tipo: TipoActivo
    moneda: Moneda
    precio_actual: DecimalMonetario = Field(gt=0)
    nivel_riesgo: int = Field(ge=1, le=5)
    activo: bool = True


class PrecioActivoSchema(BaseModel):
    precio: DecimalMonetario = Field(gt=0)
