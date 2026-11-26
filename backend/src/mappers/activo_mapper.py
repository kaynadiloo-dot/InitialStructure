from src.db.models.activo_model import Activo
from src.dtos.activo_dto import ActivoResponseDTO


def to_activo_response(activo: Activo) -> ActivoResponseDTO:
    return ActivoResponseDTO.model_validate(activo)
