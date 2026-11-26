from datetime import date
from typing import Literal

from pydantic import BaseModel, Field

from src.schemas.inversiones_tipos import DecimalMonetario, IdPositivo


class MontoTransferenciaSchema(BaseModel):
    moneda: Literal["ARS", "USD"]
    monto: DecimalMonetario = Field(gt=0)
    descripcion: str | None = Field(default=None, max_length=200)


class TransferenciaPanelSchema(MontoTransferenciaSchema):
    tipo: Literal["deposito", "extraccion"]


class OrdenCantidadSchema(BaseModel):
    activo_id: IdPositivo
    cantidad: DecimalMonetario = Field(gt=0)


class OrdenPanelSchema(OrdenCantidadSchema):
    tipo: Literal["compra", "venta"]


class TransferenciaCuentaSchema(TransferenciaPanelSchema):
    cuenta_id: IdPositivo


class OrdenCuentaSchema(OrdenPanelSchema):
    cuenta_id: IdPositivo


class MepPanelSchema(BaseModel):
    monto_ars: DecimalMonetario = Field(gt=0)


class FiltroOperacionesSchema(BaseModel):
    desde: date | None = None
    hasta: date | None = None
    tipo: Literal["compra", "venta"] | None = None
    ticker: str | None = Field(default=None, max_length=20)
