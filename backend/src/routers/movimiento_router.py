from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from src.db.connection import get_db
from src.middlewares.sesion_inversor_middleware import autorizar_ruta_inversiones
from src.dtos.movimiento_dto import CreateMovimientoDTO, MovimientoResponseDTO
from src.schemas.movimiento_schema import CreateMovimientoSchema
from src.schemas.inversiones_tipos import IdPositivo
from src.services.movimiento_service import MovimientoService
from src.schemas.panel_schema import TransferenciaCuentaSchema
from src.services.panel_service import PanelService

router = APIRouter(prefix="/movimientos", tags=["movimientos"], dependencies=[Depends(autorizar_ruta_inversiones)])


@router.post("/", response_model=MovimientoResponseDTO, status_code=status.HTTP_201_CREATED)
def create_movimiento(payload: TransferenciaCuentaSchema, db: Session = Depends(get_db)):
    return PanelService(db).transferir(payload.cuenta_id, payload.tipo, payload.moneda, payload.monto, payload.descripcion)


@router.get("/{movimiento_id}", response_model=MovimientoResponseDTO)
def get_movimiento(movimiento_id: IdPositivo, db: Session = Depends(get_db)):
    return MovimientoService(db).get_by_id(movimiento_id)

@router.put("/{movimiento_id}", response_model=MovimientoResponseDTO)
def update_movimiento(movimiento_id: IdPositivo, payload: CreateMovimientoSchema, db: Session = Depends(get_db)):
    dto = CreateMovimientoDTO(**payload.model_dump(exclude_unset=True))
    return MovimientoService(db).update(movimiento_id, dto)


@router.delete("/{movimiento_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_movimiento(movimiento_id: IdPositivo, db: Session = Depends(get_db)):
    MovimientoService(db).delete(movimiento_id)
