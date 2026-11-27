from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel

from src.dtos.panel_dto import PerfilPanelDTO


class InversorSesionDTO(BaseModel):
    nombre_cuenta: str
    nombre: str
    email: str
    cuit: str
    perfil_riesgo: str
    fecha_alta: datetime


class CuentaSesionDTO(BaseModel):
    numero_comitente: str
    saldo_ars: Decimal
    saldo_usd: Decimal


class PerfilSesionDTO(BaseModel):
    inversor: InversorSesionDTO
    cuenta: CuentaSesionDTO | None
    favoritos: list[int]

    @classmethod
    def desde_perfil(cls, perfil: PerfilPanelDTO, nombre_cuenta: str):
        return cls(
            inversor=InversorSesionDTO(nombre_cuenta=nombre_cuenta, **perfil.inversor.model_dump(exclude={"id"})),
            cuenta=CuentaSesionDTO(**perfil.cuenta.model_dump(exclude={"id", "inversor_id"})) if perfil.cuenta else None,
            favoritos=perfil.favoritos,
        )
