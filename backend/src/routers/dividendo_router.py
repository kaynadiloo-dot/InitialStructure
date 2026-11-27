from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from src.db.connection import get_db
from src.middlewares.sesion_inversor_middleware import autorizar_ruta_inversiones
from src.dtos.dividendo_dto import CreateDividendoDTO, DividendoResponseDTO
from src.schemas.dividendo_schema import CreateDividendoSchema
from src.schemas.inversiones_tipos import IdPositivo
from src.services.dividendo_service import DividendoService
from src.services.panel_service import PanelService

router = APIRouter(prefix="/dividendos", tags=["dividendos"], dependencies=[Depends(autorizar_ruta_inversiones)])


@router.post("/", response_model=DividendoResponseDTO, status_code=status.HTTP_201_CREATED)
def create_dividendo(payload: CreateDividendoSchema, db: Session = Depends(get_db)):
    dto = CreateDividendoDTO(**payload.model_dump(exclude_unset=True))
    return PanelService(db).pagar_dividendo(dto).dividendo


@router.get("/{dividendo_id}", response_model=DividendoResponseDTO)
def get_dividendo(dividendo_id: IdPositivo, db: Session = Depends(get_db)):
    return DividendoService(db).get_by_id(dividendo_id)

@router.put("/{dividendo_id}", response_model=DividendoResponseDTO)
def update_dividendo(dividendo_id: IdPositivo, payload: CreateDividendoSchema, db: Session = Depends(get_db)):
    dto = CreateDividendoDTO(**payload.model_dump(exclude_unset=True))
    return DividendoService(db).update(dividendo_id, dto)


@router.delete("/{dividendo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_dividendo(dividendo_id: IdPositivo, db: Session = Depends(get_db)):
    DividendoService(db).delete(dividendo_id)
