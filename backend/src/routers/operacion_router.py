from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from src.db.connection import get_db
from src.middlewares.sesion_inversor_middleware import autorizar_ruta_inversiones
from src.dtos.operacion_dto import CreateOperacionDTO, OperacionResponseDTO
from src.schemas.operacion_schema import CreateOperacionSchema
from src.schemas.inversiones_tipos import IdPositivo
from src.services.operacion_service import OperacionService
from src.schemas.panel_schema import OrdenCuentaSchema
from src.services.panel_service import PanelService

router = APIRouter(prefix="/operaciones", tags=["operaciones"], dependencies=[Depends(autorizar_ruta_inversiones)])


@router.post("/", response_model=OperacionResponseDTO, status_code=status.HTTP_201_CREATED)
def create_operacion(payload: OrdenCuentaSchema, db: Session = Depends(get_db)):
    return PanelService(db).operar(payload.cuenta_id, payload.activo_id, payload.tipo, payload.cantidad)


@router.get("/{operacion_id}", response_model=OperacionResponseDTO)
def get_operacion(operacion_id: IdPositivo, db: Session = Depends(get_db)):
    return OperacionService(db).get_by_id(operacion_id)

@router.put("/{operacion_id}", response_model=OperacionResponseDTO)
def update_operacion(operacion_id: IdPositivo, payload: CreateOperacionSchema, db: Session = Depends(get_db)):
    dto = CreateOperacionDTO(**payload.model_dump(exclude_unset=True))
    return OperacionService(db).update(operacion_id, dto)


@router.delete("/{operacion_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_operacion(operacion_id: IdPositivo, db: Session = Depends(get_db)):
    OperacionService(db).delete(operacion_id)
