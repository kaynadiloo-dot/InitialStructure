from decimal import Decimal

from pydantic import BaseModel


class CreateCuentaDTO(BaseModel):
    inversor_id: int
    numero_comitente: str
    saldo_ars: Decimal = Decimal("0")
    saldo_usd: Decimal = Decimal("0")


class CuentaResponseDTO(BaseModel):
    id: int
    inversor_id: int
    numero_comitente: str
    saldo_ars: Decimal
    saldo_usd: Decimal

    model_config = {"from_attributes": True}
