from decimal import Decimal

from sqlalchemy.orm import Session

from src.db.models.activo_model import Activo
from src.dtos.activo_dto import CreateActivoDTO, ActivoResponseDTO
from src.mappers.activo_mapper import to_activo_response
from src.repositories.activo_repository import ActivoRepository
from src.utils.errors import NotFoundError


class ActivoService:
    def __init__(self, db: Session):
        self.repo = ActivoRepository(db)

    def create(self, dto: CreateActivoDTO) -> ActivoResponseDTO:
        activo = self.repo.create(**dto.model_dump(exclude_unset=True))
        return to_activo_response(activo)

    def get_by_id(self, activo_id: int) -> ActivoResponseDTO:
        return to_activo_response(self._get(activo_id))

    def cambiar_precio(self, activo_id: int, precio: Decimal) -> ActivoResponseDTO:
        return to_activo_response(self.repo.update(self._get(activo_id), precio_actual=precio))

    def update(self, activo_id: int, dto: CreateActivoDTO) -> ActivoResponseDTO:
        activo = self._get(activo_id)
        actualizado = self.repo.update(activo, **dto.model_dump(exclude_unset=True))
        return to_activo_response(actualizado)

    def delete(self, activo_id: int) -> None:
        self.repo.delete(self._get(activo_id))

    def _get(self, activo_id: int) -> Activo:
        activo = self.repo.get_by_id(activo_id)
        if activo is None:
            raise NotFoundError("Activo: registro no encontrado.")
        return activo

