from sqlalchemy.orm import Session

from src.db.models.inversor_model import Inversor
from src.dtos.inversor_dto import CreateInversorDTO, InversorResponseDTO
from src.mappers.inversor_mapper import to_inversor_response
from src.repositories.inversor_repository import InversorRepository
from src.utils.errors import NotFoundError


class InversorService:
    def __init__(self, db: Session):
        self.repo = InversorRepository(db)

    def create(self, dto: CreateInversorDTO) -> InversorResponseDTO:
        inversor = self.repo.create(**dto.model_dump(exclude_unset=True))
        return to_inversor_response(inversor)

    def get_by_id(self, inversor_id: int) -> InversorResponseDTO:
        return to_inversor_response(self._get(inversor_id))

    def cambiar_perfil(self, inversor_id: int, perfil_riesgo: str) -> InversorResponseDTO:
        return to_inversor_response(self.repo.update(self._get(inversor_id), perfil_riesgo=perfil_riesgo))

    def update(self, inversor_id: int, dto: CreateInversorDTO) -> InversorResponseDTO:
        inversor = self._get(inversor_id)
        actualizado = self.repo.update(inversor, **dto.model_dump(exclude_unset=True))
        return to_inversor_response(actualizado)

    def delete(self, inversor_id: int) -> None:
        self.repo.delete(self._get(inversor_id))

    def _get(self, inversor_id: int) -> Inversor:
        inversor = self.repo.get_by_id(inversor_id)
        if inversor is None:
            raise NotFoundError("Inversor: registro no encontrado.")
        return inversor
