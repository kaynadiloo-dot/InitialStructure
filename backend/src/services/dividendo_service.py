from sqlalchemy.orm import Session

from src.db.models.dividendo_model import Dividendo
from src.dtos.dividendo_dto import CreateDividendoDTO, DividendoResponseDTO
from src.mappers.dividendo_mapper import to_dividendo_response
from src.repositories.dividendo_repository import DividendoRepository
from src.utils.errors import NotFoundError


class DividendoService:
    def __init__(self, db: Session):
        self.repo = DividendoRepository(db)

    def create(self, dto: CreateDividendoDTO) -> DividendoResponseDTO:
        dividendo = self.repo.create(**dto.model_dump(exclude_unset=True))
        return to_dividendo_response(dividendo)

    def get_by_id(self, dividendo_id: int) -> DividendoResponseDTO:
        return to_dividendo_response(self._get(dividendo_id))

    def update(self, dividendo_id: int, dto: CreateDividendoDTO) -> DividendoResponseDTO:
        dividendo = self._get(dividendo_id)
        actualizado = self.repo.update(dividendo, **dto.model_dump(exclude_unset=True))
        return to_dividendo_response(actualizado)

    def delete(self, dividendo_id: int) -> None:
        self.repo.delete(self._get(dividendo_id))

    def _get(self, dividendo_id: int) -> Dividendo:
        dividendo = self.repo.get_by_id(dividendo_id)
        if dividendo is None:
            raise NotFoundError("Dividendo: registro no encontrado.")
        return dividendo
