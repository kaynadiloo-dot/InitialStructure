from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from src.db.connection import get_db
from src.dtos.activo_dto import CreateActivoDTO, ActivoResponseDTO
from src.dtos.panel_dto import ActivoFavoritoPanelDTO, ActivoOperadoPanelDTO
from src.schemas.activo_schema import CreateActivoSchema, Moneda, PrecioActivoSchema, TipoActivo
from src.schemas.inversiones_tipos import IdPositivo
from src.services.activo_service import ActivoService
from src.services.panel_service import PanelService

router = APIRouter(prefix="/activos", tags=["activos"])


@router.get("", response_model=list[ActivoResponseDTO])
def listar_activos(tipo: TipoActivo | None = None, moneda: Moneda | None = None, db: Session = Depends(get_db)):
    return PanelService(db).activos(tipo, moneda)


@router.get("/mas-operados", response_model=list[ActivoOperadoPanelDTO])
def mas_operados(db: Session = Depends(get_db)):
    return PanelService(db).mas_operados()


@router.get("/mas-favoritos", response_model=list[ActivoFavoritoPanelDTO])
def mas_favoritos(db: Session = Depends(get_db)):
    return PanelService(db).mas_favoritos()


@router.post("/", response_model=ActivoResponseDTO, status_code=status.HTTP_201_CREATED)
@router.post("", response_model=ActivoResponseDTO, status_code=status.HTTP_201_CREATED, include_in_schema=False)
def create_activo(payload: CreateActivoSchema, db: Session = Depends(get_db)):
    dto = CreateActivoDTO(**payload.model_dump(exclude_unset=True))
    return ActivoService(db).create(dto)


@router.get("/{activo_id}", response_model=ActivoResponseDTO)
def get_activo(activo_id: IdPositivo, db: Session = Depends(get_db)):
    return ActivoService(db).get_by_id(activo_id)


@router.patch("/{activo_id}/precio", response_model=ActivoResponseDTO)
def cambiar_precio(activo_id: IdPositivo, payload: PrecioActivoSchema, db: Session = Depends(get_db)):
    return ActivoService(db).cambiar_precio(activo_id, payload.precio)

@router.put("/{activo_id}", response_model=ActivoResponseDTO)
def update_activo(activo_id: IdPositivo, payload: CreateActivoSchema, db: Session = Depends(get_db)):
    dto = CreateActivoDTO(**payload.model_dump(exclude_unset=True))
    return ActivoService(db).update(activo_id, dto)


@router.delete("/{activo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_activo(activo_id: IdPositivo, db: Session = Depends(get_db)):
    ActivoService(db).delete(activo_id)
