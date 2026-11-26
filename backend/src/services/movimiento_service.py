from sqlalchemy.orm import Session

from src.db.models.movimiento_model import Movimiento
from src.dtos.movimiento_dto import CreateMovimientoDTO, MovimientoResponseDTO
from src.mappers.movimiento_mapper import to_movimiento_response
from src.repositories.movimiento_repository import MovimientoRepository
from src.utils.errors import NotFoundError


class MovimientoService:
    def __init__(self, db: Session):
        self.repo = MovimientoRepository(db)

    def create(self, dto: CreateMovimientoDTO) -> MovimientoResponseDTO:
        movimiento = self.repo.create(**dto.model_dump(exclude_unset=True))
        return to_movimiento_response(movimiento)

    def get_by_id(self, movimiento_id: int) -> MovimientoResponseDTO:
        return to_movimiento_response(self._get(movimiento_id))

    def update(self, movimiento_id: int, dto: CreateMovimientoDTO) -> MovimientoResponseDTO:
        movimiento = self._get(movimiento_id)
        actualizado = self.repo.update(movimiento, **dto.model_dump(exclude_unset=True))
        return to_movimiento_response(actualizado)

    def delete(self, movimiento_id: int) -> None:
        self.repo.delete(self._get(movimiento_id))

    def _get(self, movimiento_id: int) -> Movimiento:
        movimiento = self.repo.get_by_id(movimiento_id)
        if movimiento is None:
            raise NotFoundError("Movimiento: registro no encontrado.")
        return movimiento
