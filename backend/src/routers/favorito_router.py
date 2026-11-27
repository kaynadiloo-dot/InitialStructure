from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from src.db.connection import get_db
from src.middlewares.sesion_inversor_middleware import autorizar_ruta_inversiones
from src.dtos.favorito_dto import CreateFavoritoDTO, FavoritoResponseDTO
from src.schemas.favorito_schema import CreateFavoritoSchema
from src.schemas.inversiones_tipos import IdPositivo
from src.services.favorito_service import FavoritoService

router = APIRouter(prefix="/favoritos", tags=["favoritos"], dependencies=[Depends(autorizar_ruta_inversiones)])


@router.post("/", response_model=FavoritoResponseDTO, status_code=status.HTTP_201_CREATED)
@router.post("", response_model=FavoritoResponseDTO, status_code=status.HTTP_201_CREATED, include_in_schema=False)
def create_favorito(payload: CreateFavoritoSchema, db: Session = Depends(get_db)):
    dto = CreateFavoritoDTO(**payload.model_dump(exclude_unset=True))
    return FavoritoService(db).create(dto)


@router.get("/{inversor_id}/{activo_id}", response_model=FavoritoResponseDTO)
def get_favorito(inversor_id: IdPositivo, activo_id: IdPositivo, db: Session = Depends(get_db)):
    return FavoritoService(db).get_by_id(inversor_id, activo_id)


@router.delete("/{inversor_id}/{activo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_favorito(inversor_id: IdPositivo, activo_id: IdPositivo, db: Session = Depends(get_db)):
    FavoritoService(db).delete(inversor_id, activo_id)
