from sqlalchemy.orm import Session

from src.db.models.cuenta_model import Cuenta
from src.dtos.cuenta_dto import CreateCuentaDTO, CuentaResponseDTO
from src.mappers.cuenta_mapper import to_cuenta_response
from src.repositories.cuenta_repository import CuentaRepository
from src.utils.errors import NotFoundError


class CuentaService:
    def __init__(self, db: Session):
        self.repo = CuentaRepository(db)

    def create(self, dto: CreateCuentaDTO) -> CuentaResponseDTO:
        cuenta = self.repo.create(**dto.model_dump(exclude_unset=True))
        return to_cuenta_response(cuenta)

    def get_by_id(self, cuenta_id: int) -> CuentaResponseDTO:
        return to_cuenta_response(self._get(cuenta_id))

    def update(self, cuenta_id: int, dto: CreateCuentaDTO) -> CuentaResponseDTO:
        cuenta = self._get(cuenta_id)
        actualizado = self.repo.update(cuenta, **dto.model_dump(exclude_unset=True))
        return to_cuenta_response(actualizado)

    def delete(self, cuenta_id: int) -> None:
        self.repo.delete(self._get(cuenta_id))

    def _get(self, cuenta_id: int) -> Cuenta:
        cuenta = self.repo.get_by_id(cuenta_id)
        if cuenta is None:
            raise NotFoundError("Cuenta: registro no encontrado.")
        return cuenta
