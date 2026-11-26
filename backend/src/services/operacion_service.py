from sqlalchemy.orm import Session

from src.db.models.operacion_model import Operacion
from src.dtos.operacion_dto import CreateOperacionDTO, OperacionResponseDTO
from src.mappers.operacion_mapper import to_operacion_response
from src.repositories.operacion_repository import OperacionRepository
from src.utils.errors import NotFoundError


class OperacionService:
    def __init__(self, db: Session):
        self.repo = OperacionRepository(db)

    def create(self, dto: CreateOperacionDTO) -> OperacionResponseDTO:
        operacion = self.repo.create(**dto.model_dump(exclude_unset=True))
        return to_operacion_response(operacion)

    def get_by_id(self, operacion_id: int) -> OperacionResponseDTO:
        return to_operacion_response(self._get(operacion_id))

    def update(self, operacion_id: int, dto: CreateOperacionDTO) -> OperacionResponseDTO:
        operacion = self._get(operacion_id)
        actualizado = self.repo.update(operacion, **dto.model_dump(exclude_unset=True))
        return to_operacion_response(actualizado)

    def delete(self, operacion_id: int) -> None:
        self.repo.delete(self._get(operacion_id))

    def _get(self, operacion_id: int) -> Operacion:
        operacion = self.repo.get_by_id(operacion_id)
        if operacion is None:
            raise NotFoundError("Operación: registro no encontrado.")
        return operacion
