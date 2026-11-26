from sqlalchemy.orm import Session

from src.db.models.tenencia_model import Tenencia
from src.dtos.tenencia_dto import CreateTenenciaDTO, TenenciaResponseDTO, UpdateTenenciaDTO
from src.mappers.tenencia_mapper import to_tenencia_response
from src.repositories.tenencia_repository import TenenciaRepository
from src.utils.errors import NotFoundError


class TenenciaService:
    def __init__(self, db: Session):
        self.repo = TenenciaRepository(db)

    def create(self, dto: CreateTenenciaDTO) -> TenenciaResponseDTO:
        tenencia = self.repo.create(**dto.model_dump(exclude_unset=True))
        return to_tenencia_response(tenencia)

    def get_by_id(self, cuenta_id: int, activo_id: int) -> TenenciaResponseDTO:
        return to_tenencia_response(self._get(cuenta_id, activo_id))

    def update(self, cuenta_id: int, activo_id: int, dto: UpdateTenenciaDTO) -> TenenciaResponseDTO:
        tenencia = self._get(cuenta_id, activo_id)
        actualizado = self.repo.update(tenencia, **dto.model_dump(exclude_unset=True))
        return to_tenencia_response(actualizado)

    def delete(self, cuenta_id: int, activo_id: int) -> None:
        self.repo.delete(self._get(cuenta_id, activo_id))

    def _get(self, cuenta_id: int, activo_id: int) -> Tenencia:
        tenencia = self.repo.get_by_id(cuenta_id, activo_id)
        if tenencia is None:
            raise NotFoundError("Tenencia: registro no encontrado.")
        return tenencia
