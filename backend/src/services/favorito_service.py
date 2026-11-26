from sqlalchemy.orm import Session

from src.db.models.favorito_model import Favorito
from src.dtos.favorito_dto import CreateFavoritoDTO, FavoritoResponseDTO
from src.mappers.favorito_mapper import to_favorito_response
from src.repositories.favorito_repository import FavoritoRepository
from src.utils.errors import NotFoundError


class FavoritoService:
    def __init__(self, db: Session):
        self.repo = FavoritoRepository(db)

    def create(self, dto: CreateFavoritoDTO) -> FavoritoResponseDTO:
        favorito = self.repo.create(**dto.model_dump(exclude_unset=True))
        return to_favorito_response(favorito)

    def get_by_id(self, inversor_id: int, activo_id: int) -> FavoritoResponseDTO:
        return to_favorito_response(self._get(inversor_id, activo_id))

    def delete(self, inversor_id: int, activo_id: int) -> None:
        self.repo.delete(self._get(inversor_id, activo_id))

    def _get(self, inversor_id: int, activo_id: int) -> Favorito:
        favorito = self.repo.get_by_id(inversor_id, activo_id)
        if favorito is None:
            raise NotFoundError("Favorito: registro no encontrado.")
        return favorito
