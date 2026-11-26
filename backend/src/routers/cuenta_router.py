from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from src.db.connection import get_db
from src.dtos.cuenta_dto import CreateCuentaDTO, CuentaResponseDTO
from src.dtos.movimiento_dto import MovimientoResponseDTO
from src.dtos.operacion_dto import OperacionResponseDTO
from src.dtos.panel_dto import CarteraPanelDTO, GananciaAnualDTO, HistorialOperacionesDTO, MepPanelDTO
from src.schemas.cuenta_schema import CreateCuentaSchema
from src.schemas.inversiones_tipos import IdPositivo
from src.schemas.panel_schema import FiltroOperacionesSchema, MepPanelSchema, MontoTransferenciaSchema, OrdenCantidadSchema
from src.services.cuenta_service import CuentaService
from src.services.panel_service import PanelService

router = APIRouter(prefix="/cuentas", tags=["cuentas"])


@router.post("/", response_model=CuentaResponseDTO, status_code=status.HTTP_201_CREATED)
def create_cuenta(payload: CreateCuentaSchema, db: Session = Depends(get_db)):
    dto = CreateCuentaDTO(**payload.model_dump(exclude_unset=True))
    return CuentaService(db).create(dto)


@router.get("/{cuenta_id}", response_model=CuentaResponseDTO)
def get_cuenta(cuenta_id: IdPositivo, db: Session = Depends(get_db)):
    return CuentaService(db).get_by_id(cuenta_id)


@router.get("/{cuenta_id}/cartera", response_model=CarteraPanelDTO)
def cartera(cuenta_id: IdPositivo, db: Session = Depends(get_db)):
    return PanelService(db).cartera(cuenta_id)


@router.get("/{cuenta_id}/movimientos", response_model=list[MovimientoResponseDTO])
def movimientos(cuenta_id: IdPositivo, db: Session = Depends(get_db)):
    return PanelService(db).movimientos(cuenta_id)


@router.get("/{cuenta_id}/operaciones", response_model=HistorialOperacionesDTO)
def historial(cuenta_id: IdPositivo, filtros: FiltroOperacionesSchema = Depends(), db: Session = Depends(get_db)):
    return PanelService(db).historial(cuenta_id, **filtros.model_dump())


@router.get("/{cuenta_id}/ganancias-realizadas", response_model=list[GananciaAnualDTO])
def ganancias_realizadas(cuenta_id: IdPositivo, db: Session = Depends(get_db)):
    return PanelService(db).ganancias(cuenta_id)


@router.post("/{cuenta_id}/depositos", response_model=MovimientoResponseDTO, status_code=status.HTTP_201_CREATED)
def depositar(cuenta_id: IdPositivo, payload: MontoTransferenciaSchema, db: Session = Depends(get_db)):
    return PanelService(db).transferir(cuenta_id, "deposito", payload.moneda, payload.monto, payload.descripcion)


@router.post("/{cuenta_id}/extracciones", response_model=MovimientoResponseDTO, status_code=status.HTTP_201_CREATED)
def extraer(cuenta_id: IdPositivo, payload: MontoTransferenciaSchema, db: Session = Depends(get_db)):
    return PanelService(db).transferir(cuenta_id, "extraccion", payload.moneda, payload.monto, payload.descripcion)


@router.post("/{cuenta_id}/compras", response_model=OperacionResponseDTO, status_code=status.HTTP_201_CREATED)
def comprar(cuenta_id: IdPositivo, payload: OrdenCantidadSchema, db: Session = Depends(get_db)):
    return PanelService(db).operar(cuenta_id, payload.activo_id, "compra", payload.cantidad)


@router.post("/{cuenta_id}/ventas", response_model=OperacionResponseDTO, status_code=status.HTTP_201_CREATED)
def vender(cuenta_id: IdPositivo, payload: OrdenCantidadSchema, db: Session = Depends(get_db)):
    return PanelService(db).operar(cuenta_id, payload.activo_id, "venta", payload.cantidad)


@router.post("/{cuenta_id}/mep", response_model=MepPanelDTO, status_code=status.HTTP_201_CREATED)
def mep(cuenta_id: IdPositivo, payload: MepPanelSchema, db: Session = Depends(get_db)):
    return PanelService(db).mep(cuenta_id, payload.monto_ars)


@router.put("/{cuenta_id}", response_model=CuentaResponseDTO)
def update_cuenta(cuenta_id: IdPositivo, payload: CreateCuentaSchema, db: Session = Depends(get_db)):
    dto = CreateCuentaDTO(**payload.model_dump(exclude_unset=True))
    return CuentaService(db).update(cuenta_id, dto)


@router.delete("/{cuenta_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_cuenta(cuenta_id: IdPositivo, db: Session = Depends(get_db)):
    CuentaService(db).delete(cuenta_id)
