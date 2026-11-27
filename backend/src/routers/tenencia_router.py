from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from src.db.connection import get_db
from src.middlewares.sesion_inversor_middleware import autorizar_ruta_inversiones
from src.dtos.tenencia_dto import CreateTenenciaDTO, TenenciaResponseDTO, UpdateTenenciaDTO
from src.schemas.tenencia_schema import CreateTenenciaSchema, UpdateTenenciaSchema
from src.schemas.inversiones_tipos import IdPositivo
from src.services.tenencia_service import TenenciaService

router = APIRouter(prefix="/tenencias", tags=["tenencias"], dependencies=[Depends(autorizar_ruta_inversiones)])


@router.post("/", response_model=TenenciaResponseDTO, status_code=status.HTTP_201_CREATED)
def create_tenencia(payload: CreateTenenciaSchema, db: Session = Depends(get_db)):
    dto = CreateTenenciaDTO(**payload.model_dump(exclude_unset=True))
    return TenenciaService(db).create(dto)


@router.get("/{cuenta_id}/{activo_id}", response_model=TenenciaResponseDTO)
def get_tenencia(cuenta_id: IdPositivo, activo_id: IdPositivo, db: Session = Depends(get_db)):
    return TenenciaService(db).get_by_id(cuenta_id, activo_id)

@router.put("/{cuenta_id}/{activo_id}", response_model=TenenciaResponseDTO)
def update_tenencia(cuenta_id: IdPositivo, activo_id: IdPositivo, payload: UpdateTenenciaSchema, db: Session = Depends(get_db)):
    dto = UpdateTenenciaDTO(**payload.model_dump(exclude_unset=True))
    return TenenciaService(db).update(cuenta_id, activo_id, dto)


@router.delete("/{cuenta_id}/{activo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_tenencia(cuenta_id: IdPositivo, activo_id: IdPositivo, db: Session = Depends(get_db)):
    TenenciaService(db).delete(cuenta_id, activo_id)
