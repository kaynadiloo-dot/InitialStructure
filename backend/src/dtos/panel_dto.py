from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel

from src.dtos.activo_dto import ActivoResponseDTO
from src.dtos.cuenta_dto import CuentaResponseDTO
from src.dtos.dividendo_dto import DividendoResponseDTO
from src.dtos.inversor_dto import InversorResponseDTO
from src.dtos.movimiento_dto import MovimientoResponseDTO
from src.dtos.operacion_dto import OperacionResponseDTO
from src.dtos.tenencia_dto import TenenciaResponseDTO


class PerfilPanelDTO(BaseModel):
    inversor: InversorResponseDTO
    cuenta: CuentaResponseDTO | None
    favoritos: list[int]


class PosicionPanelDTO(TenenciaResponseDTO):
    activo: ActivoResponseDTO
    precio_actual: Decimal
    valor_actual: Decimal
    rendimiento_porcentaje: Decimal | None


class CarteraPanelDTO(BaseModel):
    cuenta: CuentaResponseDTO
    posiciones: list[PosicionPanelDTO]
    saldos_disponibles: dict[str, Decimal]
    total_valorizado: dict[str, Decimal]
    composicion_por_tipo: dict[str, dict[str, Decimal]]


class ActividadPanelDTO(BaseModel):
    operaciones: list[OperacionResponseDTO]
    movimientos: list[MovimientoResponseDTO]


class PagoPanelDTO(BaseModel):
    dividendo: DividendoResponseDTO
    moneda: str
    cuentas_acreditadas: int
    total_pagado: Decimal


class OrdenHistorialDTO(OperacionResponseDTO):
    ticker: str
    moneda: str


class HistorialOperacionesDTO(BaseModel):
    operaciones: list[OrdenHistorialDTO]
    total_comisiones: dict[str, Decimal]


class GananciaAnualDTO(BaseModel):
    anio: int
    total_por_moneda: dict[str, Decimal]


class MepPanelDTO(BaseModel):
    compra: OperacionResponseDTO
    venta: OperacionResponseDTO
    tipo_cambio: Decimal
    monto_ars_debitado: Decimal
    monto_usd_acreditado: Decimal


class MercadoPanelDTO(BaseModel):
    abierto: bool
    hora_argentina: datetime
    horario: str


class ActivoOperadoPanelDTO(BaseModel):
    activo: ActivoResponseDTO
    unidades: Decimal


class ActivoFavoritoPanelDTO(BaseModel):
    activo: ActivoResponseDTO
    favoritos: int


class RankingsPanelDTO(BaseModel):
    operados: list[ActivoOperadoPanelDTO]
    favoritos: list[ActivoFavoritoPanelDTO]
