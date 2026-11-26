from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from src.db.connection import get_db
from src.dtos.activo_dto import ActivoResponseDTO
from src.dtos.dividendo_dto import CreateDividendoDTO
from src.dtos.inversor_dto import CreateInversorDTO
from src.dtos.movimiento_dto import MovimientoResponseDTO
from src.dtos.operacion_dto import OperacionResponseDTO
from src.dtos.panel_dto import ActividadPanelDTO, CarteraPanelDTO, MercadoPanelDTO, PagoPanelDTO, PerfilPanelDTO, RankingsPanelDTO
from src.schemas.dividendo_schema import CreateDividendoSchema
from src.schemas.inversiones_tipos import IdPositivo
from src.schemas.inversor_schema import CreateInversorSchema
from src.schemas.panel_schema import OrdenPanelSchema, TransferenciaPanelSchema
from src.services.panel_service import PanelService
from src.utils.horario_mercado import HORARIO, ahora_mercado, mercado_abierto

router = APIRouter(prefix="/panel", tags=["panel de inversiones"])


@router.get("/mercado", response_model=MercadoPanelDTO)
def estado_mercado():
    ahora = ahora_mercado()
    return MercadoPanelDTO(abierto=mercado_abierto(ahora), hora_argentina=ahora, horario=HORARIO)


@router.get("/inversores/{inversor_id}", response_model=PerfilPanelDTO)
def perfil(inversor_id: IdPositivo, db: Session = Depends(get_db)):
    return PanelService(db).perfil(inversor_id)


@router.post("/inversores", response_model=PerfilPanelDTO, status_code=status.HTTP_201_CREATED)
def alta(payload: CreateInversorSchema, db: Session = Depends(get_db)):
    return PanelService(db).alta(CreateInversorDTO(**payload.model_dump()))


@router.post("/inversores/{inversor_id}/cuenta", response_model=PerfilPanelDTO)
def abrir_cuenta(inversor_id: IdPositivo, db: Session = Depends(get_db)):
    return PanelService(db).abrir_cuenta(inversor_id)


@router.get("/activos", response_model=list[ActivoResponseDTO])
def activos(db: Session = Depends(get_db)):
    return PanelService(db).activos()


@router.get("/cuentas/{cuenta_id}/cartera", response_model=CarteraPanelDTO)
def cartera(cuenta_id: IdPositivo, db: Session = Depends(get_db)):
    return PanelService(db).cartera(cuenta_id)


@router.get("/cuentas/{cuenta_id}/actividad", response_model=ActividadPanelDTO)
def actividad(cuenta_id: IdPositivo, db: Session = Depends(get_db)):
    return PanelService(db).actividad(cuenta_id)


@router.post("/cuentas/{cuenta_id}/movimientos", response_model=MovimientoResponseDTO, status_code=status.HTTP_201_CREATED)
def transferir(cuenta_id: IdPositivo, payload: TransferenciaPanelSchema, db: Session = Depends(get_db)):
    return PanelService(db).transferir(cuenta_id, payload.tipo, payload.moneda, payload.monto, payload.descripcion)


@router.post("/cuentas/{cuenta_id}/operaciones", response_model=OperacionResponseDTO, status_code=status.HTTP_201_CREATED)
def operar(cuenta_id: IdPositivo, payload: OrdenPanelSchema, db: Session = Depends(get_db)):
    return PanelService(db).operar(cuenta_id, payload.activo_id, payload.tipo, payload.cantidad)


@router.post("/dividendos", response_model=PagoPanelDTO, status_code=status.HTTP_201_CREATED)
def pagar_dividendo(payload: CreateDividendoSchema, db: Session = Depends(get_db)):
    return PanelService(db).pagar_dividendo(CreateDividendoDTO(**payload.model_dump()))


@router.get("/rankings", response_model=RankingsPanelDTO)
def rankings(db: Session = Depends(get_db)):
    return PanelService(db).rankings()
