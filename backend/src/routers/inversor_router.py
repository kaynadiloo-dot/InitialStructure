from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from src.db.connection import get_db
from src.dtos.inversor_dto import CreateInversorDTO, InversorResponseDTO
from src.schemas.inversor_schema import CreateInversorSchema, PerfilRiesgoSchema
from src.schemas.inversiones_tipos import IdPositivo
from src.services.inversor_service import InversorService
from src.services.panel_service import PanelService

router = APIRouter(prefix="/inversores", tags=["inversores"])


@router.post("/", response_model=InversorResponseDTO, status_code=status.HTTP_201_CREATED)
@router.post("", response_model=InversorResponseDTO, status_code=status.HTTP_201_CREATED, include_in_schema=False)
def create_inversor(payload: CreateInversorSchema, db: Session = Depends(get_db)):
    return PanelService(db).alta(CreateInversorDTO(**payload.model_dump())).inversor


@router.get("/{inversor_id}", response_model=InversorResponseDTO)
def get_inversor(inversor_id: IdPositivo, db: Session = Depends(get_db)):
    return InversorService(db).get_by_id(inversor_id)


@router.patch("/{inversor_id}/perfil", response_model=InversorResponseDTO)
def cambiar_perfil(inversor_id: IdPositivo, payload: PerfilRiesgoSchema, db: Session = Depends(get_db)):
    return InversorService(db).cambiar_perfil(inversor_id, payload.perfil_riesgo)

@router.put("/{inversor_id}", response_model=InversorResponseDTO)
def update_inversor(inversor_id: IdPositivo, payload: CreateInversorSchema, db: Session = Depends(get_db)):
    dto = CreateInversorDTO(**payload.model_dump(exclude_unset=True))
    return InversorService(db).update(inversor_id, dto)


@router.delete("/{inversor_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_inversor(inversor_id: IdPositivo, db: Session = Depends(get_db)):
    InversorService(db).delete(inversor_id)
