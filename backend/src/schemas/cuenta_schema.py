from decimal import Decimal

from pydantic import BaseModel, Field

from src.schemas.inversiones_tipos import DecimalMonetario, IdPositivo


class CreateCuentaSchema(BaseModel):
    inversor_id: IdPositivo
    numero_comitente: str = Field(min_length=1, max_length=40)
    saldo_ars: DecimalMonetario = Decimal("0")
    saldo_usd: DecimalMonetario = Decimal("0")
